"""Modelos Pydantic v2 de entrada."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AuthRegisterRequest(BaseModel):
    """Solicitud para registrar un código de acceso."""

    registration_code: str = Field(min_length=6, max_length=6)


class AuthTokenRequest(BaseModel):
    """Solicitud para validar un JWT existente."""

    token: str


class ChatRequest(BaseModel):
    """Solicitud de texto desde el frontend."""

    text: str = Field(min_length=1)


class VoiceAudioRequest(BaseModel):
    """Solicitud auxiliar para flujos de voz estructurados."""

    device_id: str
    received_at: datetime | None = None


class HistoryQueryRequest(BaseModel):
    """Parámetros para consultar historial."""

    user_uuid: UUID
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
