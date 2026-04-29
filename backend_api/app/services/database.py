"""Servicios de persistencia y consulta sobre PostgreSQL."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import logging
from typing import Any

import asyncpg
from fastapi import HTTPException, status


logger = logging.getLogger(__name__)


def _row_to_dict(row: asyncpg.Record | None) -> dict[str, Any] | None:
    """Convierte un record de asyncpg a dict serializable."""

    if row is None:
        return None
    return dict(row)


def _now_utc_naive() -> datetime:
    """Devuelve una marca temporal UTC sin zona para compatibilidad con TIMESTAMP."""

    return datetime.now(timezone.utc).replace(tzinfo=None)


async def guardar_interaccion(
    conn: asyncpg.Connection,
    *,
    usuario_uuid: str | None = None,
    origen: str,
    texto_usuario: str,
    texto_respuesta: str,
    device_id: str | None = None,
    datos_extraidos: dict[str, Any] | None = None,
    reglas_resultado: dict[str, Any] | None = None,
    riesgo_resultado: dict[str, Any] | None = None,
    tts_resultado: dict[str, Any] | str | None = None,
) -> dict[str, Any]:
    """Guarda una interacción usando el esquema de Gabriela."""

    if not usuario_uuid:
        if not device_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Se requiere usuario_uuid o device_id para guardar interacción",
            )
        user_row = await conn.fetchrow(
            "SELECT uuid FROM usuarios WHERE dispositivo_id = $1 LIMIT 1",
            device_id,
        )
        if user_row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontró usuario para el device_id proporcionado",
            )
        usuario_uuid = str(user_row["uuid"])

    datos_extraidos = datos_extraidos or {}
    reglas_resultado = reglas_resultado or {}
    riesgo_resultado = riesgo_resultado or {}

    puntuacion_riesgo = riesgo_resultado.get("puntuacion_riesgo")
    if puntuacion_riesgo is None:
        puntuacion_riesgo = riesgo_resultado.get("score")

    nivel_alerta = reglas_resultado.get("nivel_alerta") or riesgo_resultado.get("nivel_alerta")
    recomendaciones = reglas_resultado.get("recomendaciones") or texto_respuesta
    fuente = reglas_resultado.get("fuente") or "orquestador"
    reglas_activadas = reglas_resultado.get("reglas_activadas") or reglas_resultado.get("reglas") or []
    requiere_accion_inmediata = bool(
        reglas_resultado.get("requiere_accion_inmediata")
        or riesgo_resultado.get("requiere_accion_inmediata")
        or False
    )

    query = """
        INSERT INTO interacciones (
            usuario_uuid,
            fecha,
            origen,
            texto_usuario,
            texto_respuesta,
            variables_extraidas,
            sintomas_madre,
            sintomas_bebe,
            nivel_alerta,
            puntuacion_riesgo,
            recomendaciones,
            fuente,
            reglas_activadas,
            requiere_accion_inmediata,
            feedback_util
        ) VALUES (
            $1, $2, $3, $4, $5, $6::jsonb, $7, $8, $9, $10, $11, $12, $13, $14, NULL
        )
        RETURNING id, usuario_uuid, fecha, origen, texto_usuario, texto_respuesta,
                  variables_extraidas, sintomas_madre, sintomas_bebe, nivel_alerta,
                  puntuacion_riesgo, recomendaciones, fuente, reglas_activadas,
                  requiere_accion_inmediata, feedback_util
    """

    record = await conn.fetchrow(
        query,
        usuario_uuid,
        _now_utc_naive(),
        origen,
        texto_usuario,
        texto_respuesta,
        json.dumps(datos_extraidos, ensure_ascii=False),
        datos_extraidos.get("sintomas_madre") or [],
        datos_extraidos.get("sintomas_bebe") or [],
        nivel_alerta,
        float(puntuacion_riesgo) if isinstance(puntuacion_riesgo, (int, float)) else None,
        recomendaciones,
        fuente,
        reglas_activadas if isinstance(reglas_activadas, list) else [],
        requiere_accion_inmediata,
    )

    logger.debug("Interacción guardada para usuario_uuid=%s device_id=%s", usuario_uuid, device_id)
    return _row_to_dict(record) or {}


async def obtener_historial(
    conn: asyncpg.Connection,
    *,
    usuario_uuid: str,
    limit: int = 50,
    offset: int = 0,
    desde: datetime | None = None,
    hasta: datetime | None = None,
    nivel_alerta: str | None = None,
    origen: str | None = None,
) -> dict[str, Any]:
    """Obtiene el historial paginado por usuaria."""

    conditions = ["usuario_uuid = $1"]
    values: list[Any] = [usuario_uuid]
    index = 2

    if desde is not None:
        conditions.append(f"fecha >= ${index}")
        values.append(desde)
        index += 1
    if hasta is not None:
        conditions.append(f"fecha <= ${index}")
        values.append(hasta)
        index += 1
    if nivel_alerta is not None:
        conditions.append(f"nivel_alerta = ${index}")
        values.append(nivel_alerta)
        index += 1
    if origen is not None:
        conditions.append(f"origen = ${index}")
        values.append(origen)
        index += 1

    where_clause = " AND ".join(conditions)

    total_row = await conn.fetchrow(
        f"SELECT COUNT(*) AS total FROM interacciones WHERE {where_clause}", *values
    )
    total = int(total_row["total"] if total_row else 0)

    rows = await conn.fetch(
        f"""
        SELECT id, usuario_uuid, fecha, origen, texto_usuario, texto_respuesta,
               variables_extraidas, sintomas_madre, sintomas_bebe, nivel_alerta,
               puntuacion_riesgo, recomendaciones, fuente, reglas_activadas,
               requiere_accion_inmediata, feedback_util
        FROM interacciones
        WHERE {where_clause}
        ORDER BY fecha DESC
        LIMIT ${index} OFFSET ${index + 1}
        """,
        *values,
        limit,
        offset,
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [dict(row) for row in rows],
    }


async def obtener_resumen_progreso(
    conn: asyncpg.Connection,
    *,
    usuario_uuid: str,
    periodo: str = "semana",
) -> dict[str, Any]:
    """Resumen agregado por periodo para progreso."""

    if periodo == "semana":
        fecha_inicio = _now_utc_naive() - timedelta(days=7)
    elif periodo == "mes":
        fecha_inicio = _now_utc_naive() - timedelta(days=30)
    elif periodo == "todo":
        fecha_inicio = datetime(2000, 1, 1)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Periodo inválido. Usa: semana, mes, todo")

    total_row = await conn.fetchrow(
        """
        SELECT COUNT(*) AS total
        FROM interacciones
        WHERE usuario_uuid = $1 AND fecha >= $2
        """,
        usuario_uuid,
        fecha_inicio,
    )

    alertas = await conn.fetchrow(
        """
        SELECT
            COUNT(*) FILTER (WHERE nivel_alerta = 'verde') AS verde,
            COUNT(*) FILTER (WHERE nivel_alerta = 'amarillo') AS amarillo,
            COUNT(*) FILTER (WHERE nivel_alerta = 'rojo') AS rojo,
            COALESCE(ROUND(AVG(puntuacion_riesgo)::numeric, 3), 0) AS riesgo_promedio,
            COUNT(*) FILTER (WHERE requiere_accion_inmediata = TRUE) AS acciones_inmediatas
        FROM interacciones
        WHERE usuario_uuid = $1 AND fecha >= $2
        """,
        usuario_uuid,
        fecha_inicio,
    )

    top_madre = await conn.fetch(
        """
        SELECT s AS sintoma, COUNT(*) AS frecuencia
        FROM interacciones, UNNEST(sintomas_madre) AS s
        WHERE usuario_uuid = $1 AND fecha >= $2
        GROUP BY s
        ORDER BY frecuencia DESC
        LIMIT 5
        """,
        usuario_uuid,
        fecha_inicio,
    )

    top_bebe = await conn.fetch(
        """
        SELECT s AS sintoma, COUNT(*) AS frecuencia
        FROM interacciones, UNNEST(sintomas_bebe) AS s
        WHERE usuario_uuid = $1 AND fecha >= $2
        GROUP BY s
        ORDER BY frecuencia DESC
        LIMIT 5
        """,
        usuario_uuid,
        fecha_inicio,
    )

    return {
        "periodo": periodo,
        "total_interacciones": int(total_row["total"] if total_row else 0),
        "alertas": {
            "verde": int(alertas["verde"] if alertas else 0),
            "amarillo": int(alertas["amarillo"] if alertas else 0),
            "rojo": int(alertas["rojo"] if alertas else 0),
        },
        "riesgo_promedio": float(alertas["riesgo_promedio"] if alertas and alertas["riesgo_promedio"] is not None else 0),
        "sintomas_madre_frecuentes": [dict(row) for row in top_madre],
        "sintomas_bebe_frecuentes": [dict(row) for row in top_bebe],
        "acciones_inmediatas": int(alertas["acciones_inmediatas"] if alertas else 0),
    }


async def obtener_datos_graficos(
    conn: asyncpg.Connection,
    *,
    usuario_uuid: str,
    agrupacion: str = "dia",
) -> dict[str, Any]:
    """Obtiene datos agregados para gráficos."""

    trunc_map = {"dia": "day", "semana": "week", "mes": "month"}
    trunc = trunc_map.get(agrupacion)
    if trunc is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Agrupación inválida. Usa: dia, semana, mes")

    rows = await conn.fetch(
        f"""
        SELECT
            DATE_TRUNC('{trunc}', fecha) AS periodo,
            COUNT(*) AS total,
            COUNT(*) FILTER (WHERE nivel_alerta = 'verde') AS verdes,
            COUNT(*) FILTER (WHERE nivel_alerta = 'amarillo') AS amarillas,
            COUNT(*) FILTER (WHERE nivel_alerta = 'rojo') AS rojas,
            AVG(puntuacion_riesgo) AS riesgo
        FROM interacciones
        WHERE usuario_uuid = $1
        GROUP BY periodo
        ORDER BY periodo ASC
        """,
        usuario_uuid,
    )

    return {
        "labels": [row["periodo"].strftime("%Y-%m-%d") for row in rows],
        "datasets": [
            {"label": "Verde", "data": [int(row["verdes"] or 0) for row in rows], "color": "#10b981"},
            {"label": "Amarillo", "data": [int(row["amarillas"] or 0) for row in rows], "color": "#f59e0b"},
            {"label": "Rojo", "data": [int(row["rojas"] or 0) for row in rows], "color": "#ef4444"},
        ],
        "riesgo_promedio": [round(float(row["riesgo"] or 0), 3) for row in rows],
    }


async def registrar_feedback(
    conn: asyncpg.Connection,
    *,
    interaccion_id: int,
    util: bool,
    usuario_uuid: str | None = None,
) -> dict[str, Any]:
    """Registra feedback verificando pertenencia a la usuaria si se proporciona UUID."""

    row = await conn.fetchrow(
        "SELECT id, usuario_uuid FROM interacciones WHERE id = $1",
        interaccion_id,
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interacción no encontrada")

    if usuario_uuid is not None and str(row["usuario_uuid"]) != str(usuario_uuid):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interacción no encontrada")

    updated = await conn.fetchrow(
        """
        UPDATE interacciones
        SET feedback_util = $1
        WHERE id = $2
        RETURNING id, usuario_uuid, fecha, origen, texto_usuario, texto_respuesta,
                  variables_extraidas, sintomas_madre, sintomas_bebe, nivel_alerta,
                  puntuacion_riesgo, recomendaciones, fuente, reglas_activadas,
                  requiere_accion_inmediata, feedback_util
        """,
        util,
        interaccion_id,
    )

    return _row_to_dict(updated) or {}
