"""Endpoints de historial de interacciones."""

import logging
from datetime import datetime

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.api.v1.models.responses import HistorialResponse, InteractionSummaryResponse
from app.core.database import get_db
from app.core.security import get_current_user
from app.services import database as database_service


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/historial", tags=["historial"])


@router.get("", response_model=HistorialResponse)
async def listar_historial(
    request: Request,
    usuario_uuid: str = Query(..., description="UUID anónimo del usuario"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    desde: datetime | None = Query(default=None),
    hasta: datetime | None = Query(default=None),
    nivel_alerta: str | None = Query(default=None),
    origen: str | None = Query(default=None),
    current_user: str = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db),
) -> HistorialResponse:
    """Devuelve el historial paginado del usuario autenticado."""

    logger.debug("Inicio request GET /historial para usuario_uuid=%s", current_user)
    try:
        if usuario_uuid != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puedes consultar el historial de otro usuario",
            )

        resultado = await database_service.obtener_historial(
            conn=conn,
            usuario_uuid=usuario_uuid,
            limit=limit,
            offset=offset,
            desde=desde,
            hasta=hasta,
            nivel_alerta=nivel_alerta,
            origen=origen,
        )

        return HistorialResponse(
            total=resultado["total"],
            limit=resultado["limit"],
            offset=resultado["offset"],
            items=[
                InteractionSummaryResponse(
                    id=item["id"],
                    user_uuid=str(item["usuario_uuid"]),
                    created_at=item["fecha"],
                    origin=item["origen"],
                    user_text=item.get("texto_usuario"),
                    assistant_text=item.get("texto_respuesta"),
                )
                for item in resultado["items"]
            ],
        )
    finally:
        logger.debug("Fin request GET /historial para usuario_uuid=%s", current_user)


@router.get("/{interaccion_id}", response_model=InteractionSummaryResponse)
async def obtener_interaccion(
    interaccion_id: int,
    current_user: str = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db),
) -> InteractionSummaryResponse:
    """Devuelve una interacción específica del usuario autenticado."""

    logger.debug("Inicio request GET /historial/%s para usuario_uuid=%s", interaccion_id, current_user)
    try:
        row = await conn.fetchrow(
            """
            SELECT id, usuario_uuid, fecha, origen, texto_usuario, texto_respuesta
            FROM interacciones
            WHERE id = $1
            """,
            interaccion_id,
        )
        if row is None or str(row["usuario_uuid"]) != current_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interacción no encontrada")

        return InteractionSummaryResponse(
            id=row["id"],
            user_uuid=str(row["usuario_uuid"]),
            created_at=row["fecha"],
            origin=row["origen"],
            user_text=row["texto_usuario"],
            assistant_text=row["texto_respuesta"],
        )
    finally:
        logger.debug("Fin request GET /historial/%s para usuario_uuid=%s", interaccion_id, current_user)
