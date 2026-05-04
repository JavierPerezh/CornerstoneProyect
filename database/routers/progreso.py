from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database import get_db
from models import Alerta, Interaccion, ProgresoDiario, Usuario
from schemas import (
    AlertaResponse,
    GraficoItem,
    ProgresoCreate,
    ProgresoResponse,
    ResumenResponse,
)

router = APIRouter(prefix="/api/v1/progreso", tags=["Progreso"])


def _get_usuario(uuid: str, db: Session) -> Usuario:
    usuario = db.execute(
        select(Usuario).where(Usuario.uuid_anonimo == uuid)
    ).scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.post("/", response_model=ProgresoResponse, status_code=201)
def registrar_progreso(data: ProgresoCreate, db: Session = Depends(get_db)):
    usuario = _get_usuario(data.uuid_anonimo, db)
    progreso = ProgresoDiario(
        usuario_id=usuario.id,
        estado_animo=data.estado_animo,
        horas_sueno=data.horas_sueno,
        notas=data.notas,
    )
    db.add(progreso)
    db.commit()
    db.refresh(progreso)
    return progreso


@router.get("/resumen", response_model=ResumenResponse)
def resumen(uuid: str = Query(...), db: Session = Depends(get_db)):
    usuario = _get_usuario(uuid, db)

    total_interacciones = db.execute(
        select(func.count()).select_from(Interaccion).where(Interaccion.usuario_id == usuario.id)
    ).scalar()

    total_alertas = db.execute(
        select(func.count()).select_from(Alerta).where(Alerta.usuario_id == usuario.id)
    ).scalar()

    ultima_alerta = db.execute(
        select(Alerta)
        .where(Alerta.usuario_id == usuario.id)
        .order_by(Alerta.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()

    promedio_animo = db.execute(
        select(func.avg(ProgresoDiario.estado_animo))
        .where(ProgresoDiario.usuario_id == usuario.id)
    ).scalar()

    registros_progreso = db.execute(
        select(func.count()).select_from(ProgresoDiario).where(ProgresoDiario.usuario_id == usuario.id)
    ).scalar()

    return ResumenResponse(
        uuid_anonimo=usuario.uuid_anonimo,
        total_interacciones=total_interacciones or 0,
        total_alertas=total_alertas or 0,
        ultima_alerta=AlertaResponse.model_validate(ultima_alerta) if ultima_alerta else None,
        promedio_animo=round(promedio_animo, 2) if promedio_animo else None,
        registros_progreso=registros_progreso or 0,
    )


@router.get("/grafico", response_model=list[GraficoItem])
def grafico(
    uuid: str = Query(...),
    limit: int = Query(default=30, ge=1, le=90),
    db: Session = Depends(get_db),
):
    usuario = _get_usuario(uuid, db)

    registros = db.execute(
        select(ProgresoDiario)
        .where(ProgresoDiario.usuario_id == usuario.id)
        .order_by(ProgresoDiario.fecha.asc())
        .limit(limit)
    ).scalars().all()

    return [
        GraficoItem(
            fecha=r.fecha.strftime("%Y-%m-%d"),
            estado_animo=r.estado_animo,
            horas_sueno=r.horas_sueno,
        )
        for r in registros
    ]
