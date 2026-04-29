"""Endpoints de autenticación."""

from datetime import datetime, timedelta, timezone
import logging

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext

from app.api.v1.models.requests import AuthRegisterRequest, AuthLoginRequest
from app.api.v1.models.responses import AuthRegisterResponse, AuthValidateTokenResponse
from app.core.database import get_db
from app.core.security import create_jwt, get_current_user


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register", response_model=AuthRegisterResponse)
async def register(
    payload: AuthRegisterRequest,
    conn: asyncpg.Connection = Depends(get_db),
) -> AuthRegisterResponse:
    """Registra al usuario mediante email y contraseña y devuelve un JWT."""

    logger.debug("Intento de registro con email=%s", payload.email)
    hashed_password = pwd_context.hash(payload.password)

    query = """
    INSERT INTO usuarios (email, password, nombre, baby_birthdate, fecha_registro)
    VALUES ($1, $2, $3, $4, $5)
    RETURNING uuid
    """
    try:
        user_record = await conn.fetchrow(
            query,
            payload.email,
            hashed_password,
            payload.nombre,
            payload.baby_birthdate,
            datetime.now(),
        )
    except asyncpg.UniqueViolationError:
        logger.debug("El email ya está registrado")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado",
        )

    usuario_uuid = str(user_record["uuid"])
    access_token = await create_jwt(usuario_uuid)
    logger.debug("Registro exitoso para usuario_uuid=%s", usuario_uuid)

    return AuthRegisterResponse(
        access_token=access_token,
        token_type="bearer",
        usuario_uuid=usuario_uuid,
    )


@router.post("/login", response_model=AuthRegisterResponse)
async def login(
    payload: AuthLoginRequest,
    conn: asyncpg.Connection = Depends(get_db),
) -> AuthRegisterResponse:
    """Autentica al usuario mediante email y contraseña y devuelve un JWT."""

    logger.debug("Intento de login con email=%s", payload.email)
    query = "SELECT uuid, password FROM usuarios WHERE email = $1 LIMIT 1"
    user_record = await conn.fetchrow(query, payload.email)

    if user_record is None or not pwd_context.verify(payload.password, user_record["password"]):
        logger.debug("Credenciales inválidas para email=%s", payload.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    usuario_uuid = str(user_record["uuid"])
    access_token = await create_jwt(usuario_uuid)
    logger.debug("Login exitoso para usuario_uuid=%s", usuario_uuid)

    return AuthRegisterResponse(
        access_token=access_token,
        token_type="bearer",
        usuario_uuid=usuario_uuid,
    )


@router.post("/token", response_model=AuthValidateTokenResponse)
async def validate_token(
    usuario_uuid: str = Depends(get_current_user),
) -> AuthValidateTokenResponse:
    """Valida el Bearer token actual y retorna su estado."""

    logger.debug("Token válido para usuario_uuid=%s", usuario_uuid)
    return AuthValidateTokenResponse(valid=True, usuario_uuid=usuario_uuid)
