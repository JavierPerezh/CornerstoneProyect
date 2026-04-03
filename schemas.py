from datetime import datetime

from pydantic import BaseModel, Field


# ── Usuarios ──────────────────────────────────────────────

class UsuarioCreate(BaseModel):
    uuid_anonimo: str
    nombre_anonimo: str | None = None
    semanas_posparto: int | None = None


class UsuarioResponse(BaseModel):
    id: int
    uuid_anonimo: str
    nombre_anonimo: str | None
    semanas_posparto: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Interacciones (historial) ─────────────────────────────

class InteraccionCreate(BaseModel):
    uuid_anonimo: str
    mensaje_usuario: str
    respuesta_bot: str


class InteraccionResponse(BaseModel):
    id: int
    usuario_id: int
    mensaje_usuario: str
    respuesta_bot: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Alertas ───────────────────────────────────────────────

class AlertaResponse(BaseModel):
    id: int
    nivel: str
    motivo: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Progreso diario ──────────────────────────────────────

class ProgresoCreate(BaseModel):
    uuid_anonimo: str
    estado_animo: int = Field(ge=1, le=5)
    horas_sueno: float | None = None
    notas: str | None = None


class ProgresoResponse(BaseModel):
    id: int
    fecha: datetime
    estado_animo: int
    horas_sueno: float | None
    notas: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ResumenResponse(BaseModel):
    uuid_anonimo: str
    total_interacciones: int
    total_alertas: int
    ultima_alerta: AlertaResponse | None
    promedio_animo: float | None
    registros_progreso: int


class GraficoItem(BaseModel):
    fecha: str
    estado_animo: int
    horas_sueno: float | None
