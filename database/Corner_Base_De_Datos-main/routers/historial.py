from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Interaccion, Usuario
from schemas import InteraccionCreate, InteraccionResponse

router = APIRouter(prefix="/api/v1/historial", tags=["Historial"])


@router.get("/", response_model=list[InteraccionResponse])
def listar_historial(
    uuid: str = Query(..., description="UUID anónimo del usuario"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    usuario = db.execute(
        select(Usuario).where(Usuario.uuid_anonimo == uuid)
    ).scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    query = (
        select(Interaccion)
        .where(Interaccion.usuario_id == usuario.id)
        .order_by(Interaccion.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.execute(query).scalars().all())


@router.post("/", response_model=InteraccionResponse, status_code=201)
def crear_interaccion(data: InteraccionCreate, db: Session = Depends(get_db)):
    usuario = db.execute(
        select(Usuario).where(Usuario.uuid_anonimo == data.uuid_anonimo)
    ).scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    interaccion = Interaccion(
        usuario_id=usuario.id,
        mensaje_usuario=data.mensaje_usuario,
        respuesta_bot=data.respuesta_bot,
    )
    db.add(interaccion)
    db.commit()
    db.refresh(interaccion)
    return interaccion
