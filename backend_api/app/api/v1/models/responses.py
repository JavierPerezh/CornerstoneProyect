"""Modelos Pydantic v2 de salida."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ChatResponse(BaseModel):
    """Respuesta estructurada del endpoint de chat."""

    model_config = ConfigDict(str_strip_whitespace=True)

    respuesta: str = Field(description="Respuesta textual generada para la madre.")
    nivel_alerta: Literal["verde", "amarillo", "rojo"] = Field(
        description="Nivel de alerta clínico asignado por el sistema.",
    )
    puntuacion_riesgo: float = Field(
        description="Puntuación de riesgo calculada para la interacción.",
    )
    requiere_accion_inmediata: bool = Field(
        description="Indica si se requiere una acción inmediata.",
    )
    recomendaciones: str = Field(
        description="Recomendaciones sugeridas para la madre.",
    )
    fuente: str = Field(
        description="Fuente principal de la respuesta (reglas, modelo, etc.).",
    )
    interaccion_id: int = Field(
        description="Identificador de la interacción guardada en base de datos.",
    )


class VozTaskResponse(BaseModel):
    """Estado de una tarea asíncrona del flujo de voz."""

    model_config = ConfigDict(str_strip_whitespace=True)

    task_id: str = Field(description="Identificador único de la tarea encolada.")
    status: Literal["procesando", "listo", "error"] = Field(
        description="Estado actual de procesamiento de la tarea de voz.",
    )
    audio_url: str | None = Field(
        default=None,
        description="URL del audio de respuesta cuando esté disponible.",
    )
    texto_respuesta: str | None = Field(
        default=None,
        description="Respuesta en texto asociada a la tarea de voz.",
    )


class HealthResponse(BaseModel):
    """Respuesta del endpoint de salud."""

    model_config = ConfigDict(str_strip_whitespace=True)

    status: str = Field(description="Estado general del servicio backend.")
    database: str = Field(description="Estado de conectividad de la base de datos.")
    timestamp: str = Field(description="Marca temporal ISO 8601 de la verificación.")


class AuthResponse(BaseModel):
    """Respuesta de autenticación con token de acceso."""

    model_config = ConfigDict(str_strip_whitespace=True)

    access_token: str = Field(description="JWT firmado para autorización del cliente.")
    token_type: str = Field(description="Tipo de token devuelto, por ejemplo bearer.")
    usuario_uuid: str = Field(description="UUID del usuario autenticado.")


class GenericMessageResponse(BaseModel):
    """Respuesta genérica para endpoints en desarrollo."""

    model_config = ConfigDict(str_strip_whitespace=True)

    message: str = Field(description="Mensaje genérico de estado u operación.")


class TaskCreatedResponse(BaseModel):
    """Respuesta para tareas en segundo plano."""

    model_config = ConfigDict(str_strip_whitespace=True)

    task_id: str = Field(description="Identificador de la tarea creada.")
    message: str = Field(
        default="Tarea encolada correctamente.",
        description="Mensaje de confirmación de creación de tarea.",
    )


class AuthTokenResponse(BaseModel):
    """Respuesta con JWT emitido por el backend."""

    model_config = ConfigDict(str_strip_whitespace=True)

    access_token: str = Field(description="JWT emitido por el backend.")
    token_type: str = Field(default="bearer", description="Tipo de token emitido.")
    expires_in_days: int = Field(
        default=30,
        ge=1,
        description="Número de días de validez del token.",
    )


class AuthRegisterResponse(BaseModel):
    """Respuesta del registro por código."""

    model_config = ConfigDict(str_strip_whitespace=True)

    access_token: str = Field(description="JWT generado tras validar el código.")
    token_type: str = Field(default="bearer", description="Tipo de token retornado.")
    usuario_uuid: str = Field(description="UUID del usuario autenticado.")


class AuthValidateTokenResponse(BaseModel):
    """Respuesta de validación de token Bearer."""

    model_config = ConfigDict(str_strip_whitespace=True)

    valid: bool = Field(description="Indica si el token recibido es válido.")
    usuario_uuid: str = Field(description="UUID extraído del token validado.")


class InteractionSummaryResponse(BaseModel):
    """Resumen de una interacción guardada en la base de datos."""

    model_config = ConfigDict(str_strip_whitespace=True)

    id: int = Field(description="Identificador interno de la interacción.")
    user_uuid: str = Field(description="UUID del usuario asociado a la interacción.")
    created_at: datetime = Field(description="Fecha y hora de creación de la interacción.")
    origin: str = Field(description="Origen de la interacción: voz o texto.")
    user_text: str | None = Field(
        default=None,
        description="Texto proporcionado por la usuaria.",
    )
    assistant_text: str | None = Field(
        default=None,
        description="Texto de respuesta generado por el asistente.",
    )


class HistorialResponse(BaseModel):
    """Respuesta paginada del historial de interacciones."""

    model_config = ConfigDict(str_strip_whitespace=True)

    total: int = Field(description="Total de interacciones encontradas.")
    limit: int = Field(description="Cantidad máxima de elementos devueltos.")
    offset: int = Field(description="Desplazamiento utilizado en la consulta.")
    items: list[InteractionSummaryResponse] = Field(
        description="Listado paginado de interacciones.",
    )


class DatoGrafico(BaseModel):
    """Datos agrupados para gráficas del progreso."""

    model_config = ConfigDict(str_strip_whitespace=True)

    labels: list[str] = Field(description="Etiquetas temporales del gráfico.")
    datasets: list[dict] = Field(description="Series de datos para renderizar el gráfico.")
    riesgo_promedio: list[float] = Field(description="Promedio de riesgo por periodo.")


class ProgresoResumen(BaseModel):
    """Resumen agregado del progreso de la usuaria."""

    model_config = ConfigDict(str_strip_whitespace=True)

    periodo: str = Field(description="Periodo consultado: semana, mes o todo.")
    total_interacciones: int = Field(description="Total de interacciones en el periodo.")
    alertas: dict = Field(description="Conteo por nivel de alerta.")
    riesgo_promedio: float = Field(description="Riesgo promedio del periodo.")
    sintomas_madre_frecuentes: list[dict] = Field(description="Síntomas de madre más frecuentes.")
    sintomas_bebe_frecuentes: list[dict] = Field(description="Síntomas de bebé más frecuentes.")
    acciones_inmediatas: int = Field(description="Cantidad de interacciones con acción inmediata.")
