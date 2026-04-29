"""Conexión y dependencia para PostgreSQL usando asyncpg."""

from collections.abc import AsyncGenerator
from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID
import logging

import asyncpg
from fastapi import FastAPI, HTTPException, Request, status
from sqlalchemy.orm import declarative_base

from app.core.config import get_settings


logger = logging.getLogger(__name__)

# SQLAlchemy ORM Base class para modelos
Base = declarative_base()


def _to_serializable(value: object) -> object:
    """Convierte tipos comunes de Postgres a valores serializables."""

    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, list):
        return [_to_serializable(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_to_serializable(item) for item in value)
    if isinstance(value, dict):
        return {key: _to_serializable(item) for key, item in value.items()}
    return value


async def create_pool(app: FastAPI) -> None:
    """Crea el pool y lo guarda en app.state.pool."""

    if getattr(app.state, "pool", None) is not None:
        logger.debug("DB pool ya inicializado en app.state.pool")
        return

    settings = get_settings()
    logger.debug("Creando DB pool con asyncpg")
    try:
        app.state.pool = await asyncpg.create_pool(dsn=settings.DATABASE_URL)
        logger.debug("DB pool creado correctamente")
    except asyncpg.PostgresError as exc:
        logging.error("Error al crear DB pool: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de base de datos no disponible.",
        ) from exc


async def close_pool(app: FastAPI) -> None:
    """Cierra el pool de forma ordenada en shutdown."""

    pool: asyncpg.Pool | None = getattr(app.state, "pool", None)
    if pool is None:
        logger.debug("No hay DB pool para cerrar")
        return

    logger.debug("Cerrando DB pool")
    try:
        await pool.close()
        app.state.pool = None
        logger.debug("DB pool cerrado correctamente")
    except asyncpg.PostgresError as exc:
        logging.error("Error al cerrar DB pool: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de base de datos no disponible.",
        ) from exc


async def get_db(request: Request) -> AsyncGenerator[asyncpg.Connection, None]:
    """Dependency que retorna una conexión adquirida del pool."""

    pool: asyncpg.Pool | None = getattr(request.app.state, "pool", None)
    if pool is None:
        logger.debug("Pool ausente en dependency get_db, recreando pool")
        await create_pool(request.app)
        pool = getattr(request.app.state, "pool", None)

    if pool is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de base de datos no disponible.",
        )

    logger.debug("Adquiriendo conexión desde el pool")
    try:
        async with pool.acquire() as connection:
            logger.debug("Conexión de base de datos adquirida")
            yield connection
            logger.debug("Conexión de base de datos liberada")
    except asyncpg.PostgresError as exc:
        logging.error("Error al adquirir/liberar conexión: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de base de datos no disponible.",
        ) from exc


async def execute_query(
    conn: asyncpg.Connection,
    query: str,
    *args: object,
) -> list[dict]:
    """Ejecuta una consulta y retorna registros serializados como dict."""

    logger.debug("Ejecutando query: %s | args=%s", query, args)
    try:
        records = await conn.fetch(query, *args)
        result = [
            {key: _to_serializable(value) for key, value in dict(record).items()}
            for record in records
        ]
        logger.debug("Query ejecutada correctamente. Filas retornadas: %s", len(result))
        return result
    except asyncpg.PostgresError as exc:
        logging.error("Error al ejecutar query: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de base de datos no disponible.",
        ) from exc
