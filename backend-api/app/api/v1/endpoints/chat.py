"""Esqueleto del endpoint de chat."""

from fastapi import APIRouter


router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/placeholder")
async def chat_placeholder() -> dict[str, str]:
    """Marcador temporal para el flujo de chat."""
    return {"message": "Endpoint de chat pendiente de implementación."}
