"""Modelos Pydantic v2 de salida."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Respuesta del endpoint de salud."""

    status: str
    environment: str


class GenericMessageResponse(BaseModel):
    """Respuesta genérica para endpoints en desarrollo."""

    message: str


class TaskCreatedResponse(BaseModel):
    """Respuesta para tareas en segundo plano."""

    task_id: str
    message: str = "Tarea encolada correctamente."


class AuthTokenResponse(BaseModel):
    """Respuesta con JWT emitido por el backend."""

    access_token: str
    token_type: str = "bearer"
    expires_in_days: int = Field(default=30, ge=1)


class InteractionSummaryResponse(BaseModel):
    """Resumen de una interacción guardada en la base de datos."""

    id: int
    user_uuid: UUID
    created_at: datetime
    origin: str
    user_text: str | None = None
    assistant_text: str | None = None
