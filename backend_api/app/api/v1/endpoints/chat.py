"""Endpoints del flujo de chat."""

import asyncio
import logging

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.v1.models.requests import ChatRequest, FeedbackRequest
from app.api.v1.models.responses import ChatResponse
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.extraccion_llm import extraer_datos
from app.services import database as database_service


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


def _require_service(services: dict, service_name: str):
    """Obtiene un servicio desde app.state.services o lanza 503."""

    service = services.get(service_name)
    if service is None:
        logger.error("Servicio '%s' no disponible en app.state.services", service_name)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Servicio no disponible: {service_name}",
        )
    return service


def _build_chat_response(
    *,
    respuesta_texto: str,
    reglas_resultado,
    riesgo_resultado,
    interaccion,
) -> ChatResponse:
    """Construye la respuesta final de chat con valores por defecto seguros."""

    nivel_alerta = "verde"
    puntuacion_riesgo = 0.0
    requiere_accion_inmediata = False
    recomendaciones = ""
    fuente = "orquestador"
    interaccion_id = 0

    if isinstance(reglas_resultado, dict):
        nivel_alerta = str(reglas_resultado.get("nivel_alerta", nivel_alerta))
        requiere_accion_inmediata = bool(
            reglas_resultado.get("requiere_accion_inmediata", requiere_accion_inmediata)
        )
        recomendaciones = str(reglas_resultado.get("recomendaciones", recomendaciones))
        fuente = str(reglas_resultado.get("fuente", fuente))

    if isinstance(riesgo_resultado, dict):
        value = riesgo_resultado.get("puntuacion_riesgo", puntuacion_riesgo)
        if isinstance(value, (int, float)):
            puntuacion_riesgo = float(value)
        if "nivel_alerta" in riesgo_resultado and riesgo_resultado["nivel_alerta"]:
            nivel_alerta = str(riesgo_resultado["nivel_alerta"])

    if isinstance(interaccion, dict):
        raw_id = interaccion.get("interaccion_id") or interaccion.get("id")
        if isinstance(raw_id, int):
            interaccion_id = raw_id
        elif isinstance(raw_id, str) and raw_id.isdigit():
            interaccion_id = int(raw_id)

    return ChatResponse(
        respuesta=respuesta_texto,
        nivel_alerta=nivel_alerta,
        puntuacion_riesgo=puntuacion_riesgo,
        requiere_accion_inmediata=requiere_accion_inmediata,
        recomendaciones=recomendaciones,
        fuente=fuente,
        interaccion_id=interaccion_id,
    )


async def _run_chat_flow(
    *,
    payload: ChatRequest,
    usuario_uuid: str,
    conn: asyncpg.Connection,
    services: dict,
) -> ChatResponse:
    """Ejecuta el pipeline síncrono de chat con manejo de errores por servicio."""

    try:
        datos_extraidos = await extraer_datos(payload.mensaje)
    except Exception as exc:
        logging.error("Error en extraer_datos para usuario_uuid=%s: %s", usuario_uuid, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Error en el servicio de extracción de datos",
        ) from exc

    motor_reglas = _require_service(services, "motor_reglas")
    risk_service = _require_service(services, "risk_service")
    respuesta_empatica = _require_service(services, "respuesta_empatica")
    try:
        reglas_resultado = await motor_reglas.evaluar(datos_extraidos)
    except Exception as exc:
        logging.error("Error en motor_reglas para usuario_uuid=%s: %s", usuario_uuid, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Error en el motor de reglas",
        ) from exc

    try:
        riesgo_resultado = await risk_service.predecir(datos_extraidos)
    except Exception as exc:
        logging.error("Error en risk_service para usuario_uuid=%s: %s", usuario_uuid, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Error en el servicio de riesgo",
        ) from exc

    try:
        respuesta_texto = await respuesta_empatica.generar(
            texto_usuario=payload.mensaje,
            datos_extraidos=datos_extraidos,
            reglas_resultado=reglas_resultado,
            riesgo_resultado=riesgo_resultado,
        )
    except Exception as exc:
        logging.error("Error en respuesta_empatica para usuario_uuid=%s: %s", usuario_uuid, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Error en el servicio de respuesta empática",
        ) from exc

    try:
        interaccion = await database_service.guardar_interaccion(
            conn=conn,
            usuario_uuid=usuario_uuid,
            origen="texto",
            texto_usuario=payload.mensaje,
            texto_respuesta=respuesta_texto,
            datos_extraidos=datos_extraidos,
            reglas_resultado=reglas_resultado,
            riesgo_resultado=riesgo_resultado,
        )
    except Exception as exc:
        logging.error(
            "Error en database_service.guardar_interaccion usuario_uuid=%s: %s",
            usuario_uuid,
            exc,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Error al guardar la interacción",
        ) from exc

    return _build_chat_response(
        respuesta_texto=respuesta_texto,
        reglas_resultado=reglas_resultado,
        riesgo_resultado=riesgo_resultado,
        interaccion=interaccion,
    )


@router.post("", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    request: Request,
    usuario_uuid: str = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db),
) -> ChatResponse:
    """Procesa una interacción de texto y responde de forma síncrona."""

    logger.debug("Inicio request POST /chat para usuario_uuid=%s", usuario_uuid)
    try:
        if payload.usuario_uuid != usuario_uuid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario del token no coincide con el body",
            )

        services = getattr(request.app.state, "services", {})
        try:
            return await asyncio.wait_for(
                _run_chat_flow(
                    payload=payload,
                    usuario_uuid=usuario_uuid,
                    conn=conn,
                    services=services,
                ),
                timeout=30,
            )
        except TimeoutError as exc:
            logging.error("Timeout total de 30s en POST /chat para usuario_uuid=%s", usuario_uuid, exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="El procesamiento de chat excedió el tiempo máximo",
            ) from exc
    finally:
        logger.debug("Fin request POST /chat para usuario_uuid=%s", usuario_uuid)


@router.post("/feedback")
async def chat_feedback(
    payload: FeedbackRequest,
    request: Request,
    usuario_uuid: str = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db),
) -> dict[str, bool]:
    """Registra feedback de utilidad de una interacción del usuario autenticado."""

    logger.debug("Inicio request POST /chat/feedback para usuario_uuid=%s", usuario_uuid)
    try:
        row = await conn.fetchrow(
            "SELECT usuario_uuid FROM interacciones WHERE id = $1",
            payload.interaccion_id,
        )
        if row is None or str(row["usuario_uuid"]) != usuario_uuid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interacción no encontrada",
            )

        try:
            await database_service.registrar_feedback(
                interaccion_id=payload.interaccion_id,
                util=payload.util,
                conn=conn,
                usuario_uuid=usuario_uuid,
            )
        except Exception as exc:
            logging.error(
                "Error en database_service.registrar_feedback interaccion_id=%s usuario_uuid=%s: %s",
                payload.interaccion_id,
                usuario_uuid,
                exc,
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Error al registrar feedback",
            ) from exc

        return {"success": True}
    finally:
        logger.debug("Fin request POST /chat/feedback para usuario_uuid=%s", usuario_uuid)
