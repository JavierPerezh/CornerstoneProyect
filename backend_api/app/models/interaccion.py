from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Interaccion(Base):
    __tablename__ = "interacciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_uuid = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.uuid", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    fecha = Column(DateTime, server_default=func.now(), index=True)
    origen = Column(String(10))
    texto_usuario = Column(Text, nullable=False)
    texto_respuesta = Column(Text, nullable=False)
    variables_extraidas = Column(JSON, nullable=True)
    sintomas_madre = Column(ARRAY(String), nullable=True)
    sintomas_bebe = Column(ARRAY(String), nullable=True)
    nivel_alerta = Column(String(10), nullable=True)
    puntuacion_riesgo = Column(Float, nullable=True)
    recomendaciones = Column(Text, nullable=True)
    fuente = Column(Text, nullable=True)
    reglas_activadas = Column(ARRAY(String), nullable=True)
    requiere_accion_inmediata = Column(Boolean, default=False)
    feedback_util = Column(Boolean, nullable=True)

    usuario = relationship("Usuario", back_populates="interacciones")
