from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator


class InteraccionCreate(BaseModel):
    usuario_uuid: str
    origen: Optional[str] = "texto"
    texto_usuario: str
    texto_respuesta: str
    variables_extraidas: Optional[dict] = None
    sintomas_madre: Optional[List[str]] = None
    sintomas_bebe: Optional[List[str]] = None
    nivel_alerta: Optional[str] = None
    puntuacion_riesgo: Optional[float] = None
    recomendaciones: Optional[str] = None
    fuente: Optional[str] = None
    reglas_activadas: Optional[List[str]] = None
    requiere_accion_inmediata: Optional[bool] = False

    @field_validator("usuario_uuid", mode="before")
    @classmethod
    def uuid_to_str(cls, v):
        return str(v) if v is not None else v


class InteraccionResponse(InteraccionCreate):
    id: int
    fecha: datetime
    feedback_util: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class FeedbackUpdate(BaseModel):
    util: bool


class HistorialResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[InteraccionResponse]
