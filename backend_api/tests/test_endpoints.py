"""Pruebas de integración de endpoints principales."""

import importlib

import pytest


@pytest.mark.asyncio
async def test_health_ok(async_client):
    """GET /health debe responder estado ok."""

    response = await async_client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"


@pytest.mark.asyncio
async def test_auth_register_valid_code_returns_jwt(async_client):
    """POST /api/v1/auth/register con código válido debe devolver JWT."""

    response = await async_client.post("/api/v1/auth/register", json={"codigo_registro": "123456"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert isinstance(payload["access_token"], str)
    assert payload["access_token"]
    assert isinstance(payload["usuario_uuid"], str)


@pytest.mark.asyncio
async def test_auth_register_invalid_code_returns_404(async_client):
    """POST /api/v1/auth/register con código inválido debe responder 404."""

    response = await async_client.post("/api/v1/auth/register", json={"codigo_registro": "000000"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_voz_without_device_header_returns_401(async_client):
    """POST /api/v1/voz sin X-Device-Id debe responder 401."""

    files = {"audio": ("audio.wav", b"RIFF....WAVE", "audio/wav")}
    response = await async_client.post("/api/v1/voz", files=files)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_voz_invalid_device_returns_401(async_client):
    """POST /api/v1/voz con device_id inválido debe responder 401."""

    files = {"audio": ("audio.wav", b"RIFF....WAVE", "audio/wav")}
    response = await async_client.post(
        "/api/v1/voz",
        files=files,
        headers={"X-Device-Id": "device-invalid-999"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_chat_without_jwt_returns_401(async_client):
    """POST /api/v1/chat sin Authorization debe responder 401."""

    response = await async_client.post(
        "/api/v1/chat",
        json={"mensaje": "hola", "usuario_uuid": "user-1"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_chat_with_valid_jwt_returns_200(async_client):
    """POST /api/v1/chat con JWT válido y payload válido debe responder 200."""

    security_module = importlib.import_module("app.core.security")
    usuario_uuid = "2b8be7e4-6d17-4f0d-8a2c-f4b3d86f1b0d"
    token = await security_module.create_jwt(usuario_uuid)

    response = await async_client.post(
        "/api/v1/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"mensaje": "Me siento algo cansada hoy", "usuario_uuid": usuario_uuid},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "respuesta" in payload
    assert payload["interaccion_id"] == 2
