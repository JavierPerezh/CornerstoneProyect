from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid_anonimo: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    nombre_anonimo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    semanas_posparto: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    interacciones: Mapped[list["Interaccion"]] = relationship(back_populates="usuario", cascade="all, delete-orphan")
    alertas: Mapped[list["Alerta"]] = relationship(back_populates="usuario", cascade="all, delete-orphan")
    progresos: Mapped[list["ProgresoDiario"]] = relationship(back_populates="usuario", cascade="all, delete-orphan")


class Interaccion(Base):
    __tablename__ = "interacciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"))
    mensaje_usuario: Mapped[str] = mapped_column(Text)
    respuesta_bot: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    usuario: Mapped["Usuario"] = relationship(back_populates="interacciones")


class Alerta(Base):
    __tablename__ = "alertas"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"))
    nivel: Mapped[str] = mapped_column(String(10))
    motivo: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    usuario: Mapped["Usuario"] = relationship(back_populates="alertas")

    __table_args__ = (
        CheckConstraint("nivel IN ('verde', 'amarillo', 'rojo')", name="ck_alerta_nivel"),
    )


class ProgresoDiario(Base):
    __tablename__ = "progreso_diario"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"))
    fecha: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    estado_animo: Mapped[int] = mapped_column(Integer)  # 1-5
    horas_sueno: Mapped[float | None] = mapped_column(nullable=True)
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    usuario: Mapped["Usuario"] = relationship(back_populates="progresos")
