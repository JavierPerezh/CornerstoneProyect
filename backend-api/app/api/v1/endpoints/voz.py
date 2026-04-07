"""Esqueleto del endpoint de voz."""

from fastapi import APIRouter


router = APIRouter(prefix="/voz", tags=["voz"])


@router.get("/placeholder")
async def voz_placeholder() -> dict[str, str]:
    """Marcador temporal para el flujo de voz."""
    return {"message": "Endpoint de voz pendiente de implementación."}
