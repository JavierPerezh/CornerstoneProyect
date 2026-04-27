"""Endpoints de autenticación."""

from datetime import datetime, timedelta, timezone
import logging

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.models.requests import AuthRegisterRequest
from app.api.v1.models.responses import AuthRegisterResponse, AuthValidateTokenResponse
from app.core.database import get_db
from app.core.security import create_jwt, get_current_user


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthRegisterResponse)
async def register(
    payload: AuthRegisterRequest,
    conn: asyncpg.Connection = Depends(get_db),
) -> AuthRegisterResponse:
    """Registra al usuario mediante código de 6 dígitos y devuelve un JWT."""

    logger.debug("Intento de registro con codigo_registro=%s", payload.codigo_registro)
    query = "SELECT uuid, fecha_registro FROM usuarios WHERE codigo_registro = $1 LIMIT 1"
    user_record = await conn.fetchrow(query, payload.codigo_registro)

    if user_record is None:
        logger.debug("Código de registro no encontrado")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Código de registro no encontrado o expirado",
        )

    fecha_registro: datetime = user_record["fecha_registro"]
    if fecha_registro.tzinfo is None:
        fecha_registro = fecha_registro.replace(tzinfo=timezone.utc)

    expiration_limit = fecha_registro + timedelta(hours=24)
    if datetime.now(timezone.utc) > expiration_limit:
        logger.debug("Código de registro expirado para usuario_uuid=%s", user_record["uuid"])
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Código de registro no encontrado o expirado",
        )

    usuario_uuid = str(user_record["uuid"])
    access_token = await create_jwt(usuario_uuid)
    logger.debug("Registro exitoso para usuario_uuid=%s", usuario_uuid)

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
