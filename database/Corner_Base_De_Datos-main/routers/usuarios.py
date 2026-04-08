from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Usuario
from schemas import UsuarioCreate, UsuarioResponse

router = APIRouter(prefix="/api/v1/usuarios", tags=["Usuarios"])


@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.execute(select(Usuario).order_by(Usuario.created_at.desc())).scalars().all()
    return list(usuarios)


@router.post("/", response_model=UsuarioResponse, status_code=201)
def crear_usuario(data: UsuarioCreate, db: Session = Depends(get_db)):
    existe = db.execute(
        select(Usuario).where(Usuario.uuid_anonimo == data.uuid_anonimo)
    ).scalar_one_or_none()
    if existe:
        raise HTTPException(status_code=400, detail="El UUID ya está registrado")
    usuario = Usuario(**data.model_dump())
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario
