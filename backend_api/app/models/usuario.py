import uuid

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dispositivo_id = Column(String(50), unique=True, nullable=True)
    codigo_registro = Column(String(6), nullable=True)
    fecha_registro = Column(DateTime, server_default=func.now())
    fecha_consentimiento = Column(DateTime, nullable=True)
    anonimizado = Column(Boolean, default=False)
    fecha_anonimizacion = Column(DateTime, nullable=True)

    interacciones = relationship(
        "Interaccion", back_populates="usuario", cascade="all, delete"
    )
