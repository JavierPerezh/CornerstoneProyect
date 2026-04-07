"""Agrupa los routers de la versión 1."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, chat, historial, voz


router = APIRouter()
router.include_router(voz.router)
router.include_router(chat.router)
router.include_router(auth.router)
router.include_router(historial.router)
