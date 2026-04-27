"""Configuración compartida para pruebas."""

import importlib
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import AsyncGenerator
from uuid import uuid4

import pytest
import pytest_asyncio
from dotenv import dotenv_values
from httpx import ASGITransport, AsyncClient


ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_TEST_FILE = ROOT_DIR / ".env.test"


@dataclass
class FakeTestDB:
    """BD de prueba en memoria para fixtures de endpoints."""

    users_by_code: dict[str, dict] = field(default_factory=dict)
    users_by_device: dict[str, dict] = field(default_factory=dict)
    interacciones: dict[int, dict] = field(default_factory=dict)


class FakeConnection:
    """Conexión fake compatible con métodos usados por endpoints."""

    def __init__(self, test_db: FakeTestDB):
        self._db = test_db

    async def fetchrow(self, query: str, *args):
        normalized_query = " ".join(query.lower().split())

        if "from usuarios where codigo_registro" in normalized_query:
            code = args[0]
            return self._db.users_by_code.get(code)

        if "from usuarios where dispositivo_id" in normalized_query:
            device_id = args[0]
            return self._db.users_by_device.get(device_id)

        if "from interacciones where id" in normalized_query:
            interaction_id = args[0]
            return self._db.interacciones.get(interaction_id)

        if "insert into interacciones" in normalized_query:
            next_id = max(self._db.interacciones.keys(), default=0) + 1
            record = {
                "id": next_id,
                "usuario_uuid": args[0],
                "fecha": args[1],
                "origen": args[2],
                "texto_usuario": args[3],
                "texto_respuesta": args[4],
                "variables_extraidas": args[5],
                "sintomas_madre": args[6],
                "sintomas_bebe": args[7],
                "nivel_alerta": args[8],
                "puntuacion_riesgo": args[9],
                "recomendaciones": args[10],
                "fuente": args[11],
                "reglas_activadas": args[12],
                "requiere_accion_inmediata": args[13],
                "feedback_util": None,
            }
            self._db.interacciones[next_id] = record
            return record

        if "update interacciones" in normalized_query:
            util = args[0]
            interaction_id = args[1]
            record = self._db.interacciones.get(interaction_id)
            if record is None:
                return None
            record["feedback_util"] = util
            return record

        return None


class MockMotorReglas:
    """Mock del motor de reglas."""

    async def evaluar(self, _datos):
        return {
            "nivel_alerta": "verde",
            "requiere_accion_inmediata": False,
            "recomendaciones": "Mantener hidratacion y descanso.",
            "fuente": "motor_reglas",
        }


class MockRiskService:
    """Mock del servicio de riesgo."""

    async def predecir(self, _datos):
        return {"puntuacion_riesgo": 0.12, "nivel_alerta": "verde"}


class MockRespuestaEmpatica:
    """Mock del servicio de respuesta empática."""

    async def generar(self, **_kwargs):
        return "Te entiendo, vamos paso a paso para ayudarte."


class MockTTS:
    """Mock de TTS para completar app.state.services."""

    async def convertir(self, _texto):
        return {"audio_url": "https://example.test/audio/mock.wav"}


class MockDatabaseService:
    """Mock del servicio de persistencia."""

    async def guardar_interaccion(self, **_kwargs):
        return {"id": 1}

    async def registrar_feedback(self, *args, **kwargs):
        return {"ok": True, "args": args, "kwargs": kwargs}


@pytest.fixture(scope="session", autouse=True)
def load_test_environment() -> None:
    """Carga variables desde .env.test para aislar el entorno de pruebas."""

    if ENV_TEST_FILE.exists():
        values = dotenv_values(ENV_TEST_FILE)
        for key, value in values.items():
            if value is not None:
                os.environ[key] = value

    os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test_db")
    os.environ.setdefault("GROQ_API_KEY", "test-groq-key")
    os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
    os.environ.setdefault("DEVICE_API_KEY_SECRET", "test-device-secret")
    os.environ.setdefault("JWT_SECRET", "test-jwt-secret")
    os.environ.setdefault("JWT_EXPIRE_DAYS", "30")
    os.environ.setdefault("ENVIRONMENT", "test")
    os.environ.setdefault("STATIC_AUDIO_DIR", "static/audio")


@pytest.fixture
def test_db() -> FakeTestDB:
    """Crea datos base para pruebas de endpoints."""

    now = datetime.now(timezone.utc)
    valid_user_uuid = str(uuid4())
    valid_user = {
        "uuid": valid_user_uuid,
        "fecha_registro": now - timedelta(hours=1),
        "dispositivo_id": "device-valid-001",
        "codigo_registro": "123456",
    }

    db = FakeTestDB(
        users_by_code={"123456": valid_user},
        users_by_device={"device-valid-001": valid_user},
        interacciones={1: {"usuario_uuid": valid_user_uuid}},
    )
    return db


@pytest_asyncio.fixture
async def app_instance(monkeypatch: pytest.MonkeyPatch, test_db: FakeTestDB):
    """Instancia de FastAPI configurada para pruebas."""

    app_main = importlib.import_module("app.main")
    security_module = importlib.import_module("app.core.security")
    database_module = importlib.import_module("app.core.database")
    chat_endpoint_module = importlib.import_module("app.api.v1.endpoints.chat")

    async def _fake_create_pool(app):
        app.state.pool = object()

    async def _fake_close_pool(app):
        app.state.pool = None

    async def _override_get_db() -> AsyncGenerator[FakeConnection, None]:
        yield FakeConnection(test_db)

    async def _fake_extraer_datos(_mensaje: str) -> dict:
        return {
            "sintomas_madre": ["dolor de cabeza"],
            "sintomas_bebe": [],
            "duracion_horas": 2.0,
            "intensidad": 4,
            "estado_emocional": "ansiosa",
            "contexto_adicional": "Prueba de extraccion",
        }

    monkeypatch.setattr(app_main, "create_pool", _fake_create_pool)
    monkeypatch.setattr(app_main, "close_pool", _fake_close_pool)
    monkeypatch.setattr(chat_endpoint_module, "extraer_datos", _fake_extraer_datos)

    app = app_main.app
    app.state.services = {
        "motor_reglas": MockMotorReglas(),
        "risk_service": MockRiskService(),
        "respuesta_empatica": MockRespuestaEmpatica(),
        "database_service": MockDatabaseService(),
        "tts": MockTTS(),
    }
    app.dependency_overrides[database_module.get_db] = _override_get_db

    # Limpia memoria compartida del store de tareas entre pruebas.
    colas_module = importlib.import_module("app.services.colas")
    colas_module.TASK_STORE.clear()

    yield app

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(app_instance):
    """Cliente HTTP asíncrono para probar la app ASGI."""

    transport = ASGITransport(app=app_instance)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
