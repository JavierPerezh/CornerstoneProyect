"""Endpoints del flujo de voz."""

import logging

import asyncpg
from fastapi import APIRouter, BackgroundTasks, Depends, File, Header, HTTPException, Request, UploadFile, status

from app.api.v1.models.responses import VozTaskResponse
from app.core.database import get_db
from app.core.security import validate_device
from app.services import colas


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voz", tags=["voz"])

MAX_AUDIO_BYTES = 10 * 1024 * 1024
ALLOWED_AUDIO_TYPES = {"audio/wav", "audio/x-wav"}


@router.post("", response_model=VozTaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def crear_tarea_voz(
    request: Request,
    background_tasks: BackgroundTasks,
    audio: UploadFile = File(...),
    device_id: str | None = Header(default=None, alias="X-Device-Id"),
    conn: asyncpg.Connection = Depends(get_db),
) -> VozTaskResponse:
    """Recibe audio WAV, encola procesamiento y retorna task_id inmediato."""

    logger.debug("Inicio request POST /voz con device_id=%s", device_id)
    try:
        if not device_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Header X-Device-Id requerido",
            )

        await validate_device(device_id, conn)

        if audio.content_type not in ALLOWED_AUDIO_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="El archivo debe ser WAV (audio/wav o audio/x-wav)",
            )

        audio_bytes = await audio.read()
        if len(audio_bytes) > MAX_AUDIO_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="El archivo supera el tamaño máximo permitido de 10MB",
            )

        task_id = colas.crear_tarea()
        services = getattr(request.app.state, "services", {})
        background_tasks.add_task(
            colas.procesar_audio,
            task_id,
            audio_bytes,
            device_id,
            conn,
            services,
        )

        return VozTaskResponse(task_id=task_id, status="procesando")
    finally:
        logger.debug("Fin request POST /voz con device_id=%s", device_id)


@router.get("/status/{task_id}", response_model=VozTaskResponse)
async def obtener_estado_voz(
    task_id: str,
    device_id: str | None = Header(default=None, alias="X-Device-Id"),
    conn: asyncpg.Connection = Depends(get_db),
) -> VozTaskResponse:
    """Retorna el estado actual de una tarea de voz."""

    logger.debug("Inicio request GET /voz/status/%s con device_id=%s", task_id, device_id)
    try:
        if not device_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Header X-Device-Id requerido",
            )

        await validate_device(device_id, conn)

        task_data = colas.obtener_tarea(task_id)
        if task_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada",
            )

        return VozTaskResponse(
            task_id=str(task_data.get("task_id", task_id)),
            status=task_data.get("status", "error"),
            audio_url=task_data.get("audio_url"),
            texto_respuesta=task_data.get("texto_respuesta"),
        )
    finally:
        logger.debug("Fin request GET /voz/status/%s con device_id=%s", task_id, device_id)
