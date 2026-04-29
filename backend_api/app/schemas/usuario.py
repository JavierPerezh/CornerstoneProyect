from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class UsuarioCreate(BaseModel):
    dispositivo_id: Optional[str] = None
    codigo_registro: Optional[str] = None


class UsuarioResponse(BaseModel):
    uuid: str
    dispositivo_id: Optional[str]
    codigo_registro: Optional[str]
    fecha_registro: datetime
    fecha_consentimiento: Optional[datetime]
    anonimizado: bool
    fecha_anonimizacion: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

    @field_validator("uuid", mode="before")
    @classmethod
    def uuid_to_str(cls, v):
        return str(v) if v is not None else v
