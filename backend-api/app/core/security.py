"""Utilidades de autenticación y autorización."""

from datetime import datetime, timedelta, timezone
import logging

import asyncpg
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import get_settings


logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer(auto_error=False)


async def validate_device(device_id: str, conn: asyncpg.Connection) -> dict:
	"""Valida un dispositivo contra la tabla usuarios y retorna su registro."""

	logger.debug("Validando dispositivo con id=%s", device_id)
	query = "SELECT * FROM usuarios WHERE dispositivo_id = $1 LIMIT 1"
	record = await conn.fetchrow(query, device_id)

	if record is None:
		logger.debug("Dispositivo no registrado: id=%s", device_id)
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Dispositivo no registrado",
		)

	logger.debug("Dispositivo validado correctamente: id=%s", device_id)
	return dict(record)


async def create_jwt(usuario_uuid: str) -> str:
	"""Genera un JWT firmado para un usuario."""

	settings = get_settings()
	now = datetime.now(timezone.utc)
	expire_at = now + timedelta(days=settings.JWT_EXPIRE_DAYS)

	payload = {
		"sub": usuario_uuid,
		"iat": int(now.timestamp()),
		"exp": int(expire_at.timestamp()),
	}

	logger.debug("Creando JWT para usuario_uuid=%s", usuario_uuid)
	token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
	logger.debug("JWT creado correctamente para usuario_uuid=%s", usuario_uuid)
	return token


async def validate_jwt(token: str) -> str:
	"""Valida un JWT y retorna el usuario_uuid del claim sub."""

	settings = get_settings()
	logger.debug("Validando JWT recibido")
	try:
		payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
		usuario_uuid = payload.get("sub")
		if not usuario_uuid:
			logger.debug("JWT inválido: claim sub ausente")
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Token inválido o expirado",
			)

		logger.debug("JWT válido para usuario_uuid=%s", usuario_uuid)
		return str(usuario_uuid)
	except JWTError as exc:
		logger.debug("JWT inválido o expirado: %s", exc)
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Token inválido o expirado",
		) from exc


async def get_current_user(
	credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
	"""Dependency que retorna el usuario autenticado desde Authorization Bearer."""

	if credentials is None or credentials.scheme.lower() != "bearer":
		logger.debug("Authorization Bearer ausente o inválido")
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Token inválido o expirado",
		)

	return await validate_jwt(credentials.credentials)
