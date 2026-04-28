"""Endpoints de progreso y analítica."""

import logging

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.v1.models.responses import DatoGrafico, ProgresoResumen
from app.core.database import get_db
from app.core.security import get_current_user
from app.services import database as database_service


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/progreso", tags=["progreso"])


@router.get("/resumen", response_model=ProgresoResumen)
async def resumen(
    usuario_uuid: str = Query(...),
    periodo: str = Query(default="semana", pattern="^(semana|mes|todo)$"),
    current_user: str = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db),
) -> ProgresoResumen:
    """Devuelve el resumen agregado del progreso del usuario autenticado."""

    if usuario_uuid != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes consultar el progreso de otro usuario",
        )

    resultado = await database_service.obtener_resumen_progreso(
        conn=conn,
        usuario_uuid=usuario_uuid,
        periodo=periodo,
    )
    return ProgresoResumen.model_validate(resultado)


@router.get("/grafico", response_model=DatoGrafico)
async def grafico(
    usuario_uuid: str = Query(...),
    agrupacion: str = Query(default="dia", pattern="^(dia|semana|mes)$"),
    current_user: str = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db),
) -> DatoGrafico:
    """Devuelve datos de gráfica del progreso del usuario autenticado."""

    if usuario_uuid != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes consultar el progreso de otro usuario",
        )

    resultado = await database_service.obtener_datos_graficos(
        conn=conn,
        usuario_uuid=usuario_uuid,
        agrupacion=agrupacion,
    )
    return DatoGrafico.model_validate(resultado)
