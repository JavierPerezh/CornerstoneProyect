"""Esqueleto del endpoint de autenticación."""

from fastapi import APIRouter


router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/placeholder")
async def auth_placeholder() -> dict[str, str]:
    """Marcador temporal para el flujo de autenticación."""
    return {"message": "Endpoint de auth pendiente de implementación."}
