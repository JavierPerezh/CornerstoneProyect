"""Modelos Pydantic v2 de entrada."""

from pydantic import BaseModel, ConfigDict, Field


class AuthRegisterRequest(BaseModel):
    """Solicitud para registrar un código de acceso."""

    model_config = ConfigDict(str_strip_whitespace=True)

    codigo_registro: str = Field(
        min_length=6,
        max_length=6,
        description="Código de registro de 6 caracteres entregado al usuario.",
    )


class AuthTokenRequest(BaseModel):
    """Solicitud para validar un JWT existente."""

    model_config = ConfigDict(str_strip_whitespace=True)

    token: str = Field(description="Token JWT a validar.")


class ChatRequest(BaseModel):
    """Solicitud de mensaje de chat enviada por el frontend."""

    model_config = ConfigDict(str_strip_whitespace=True)

    mensaje: str = Field(
        min_length=1,
        max_length=1000,
        description="Mensaje de texto enviado por la madre.",
    )
    usuario_uuid: str = Field(
        description="Identificador UUID del usuario que envía el mensaje.",
    )


class FeedbackRequest(BaseModel):
    """Solicitud para registrar feedback sobre una interacción previa."""

    model_config = ConfigDict(str_strip_whitespace=True)

    interaccion_id: int = Field(description="Identificador de la interacción evaluada.")
    util: bool = Field(description="Indica si la respuesta fue útil para la usuaria.")
