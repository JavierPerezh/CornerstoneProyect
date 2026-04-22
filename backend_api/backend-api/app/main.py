"""Punto de entrada principal de FastAPI."""

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.models.responses import HealthResponse
from app.api.v1.router import router as api_v1_router
from app.core.config import get_settings
from app.core.database import close_pool, create_pool


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona el ciclo de vida de la aplicación."""
    await create_pool(app)
    yield
    await close_pool(app)


app = FastAPI(
    title="Backend Principal",
    version="1.0.0",
    lifespan=lifespan,
)

allowed_origins = ["http://localhost:3000"]
allow_credentials = True
if settings.ENVIRONMENT.lower() in {"dev", "development", "local"}:
    allowed_origins = ["*"]
    allow_credentials = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check(request: Request) -> HealthResponse:
    """Verifica que el servicio esté disponible."""
    db_status = "ok" if getattr(request.app.state, "pool", None) is not None else "down"
    return HealthResponse(
        status="ok",
        database=db_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
