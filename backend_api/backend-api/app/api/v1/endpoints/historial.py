"""Esqueleto del endpoint de historial."""

from fastapi import APIRouter


router = APIRouter(prefix="/historial", tags=["historial"])


@router.get("/placeholder")
async def historial_placeholder() -> dict[str, str]:
    """Marcador temporal para el historial de interacciones."""
    return {"message": "Endpoint de historial pendiente de implementación."}
