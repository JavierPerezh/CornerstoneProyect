"""Pruebas unitarias de servicios de IA con mocks."""

from types import SimpleNamespace

import pytest

from app.services import extraccion_llm, transcripcion


@pytest.mark.asyncio
async def test_transcribir_audio_elimina_temporal(mocker, tmp_path):
    """Verifica que transcribir_audio elimine el archivo temporal al terminar."""

    audio_path = tmp_path / "audio_test.wav"
    audio_path.write_bytes(b"fake wav bytes")

    mocker.patch.object(
        transcripcion,
        "_transcribe_with_whisper",
        return_value="hola mundo",
    )

    result = await transcripcion.transcribir_audio(str(audio_path))

    assert result == "hola mundo"
    assert not audio_path.exists()


@pytest.mark.asyncio
async def test_extraer_datos_parsea_json_correcto(mocker):
    """Verifica parseo correcto cuando Groq retorna JSON válido."""

    class FakeCompletions:
        async def create(self, **_kwargs):
            content = (
                '{"sintomas_madre":["dolor de cabeza"],"sintomas_bebe":[],"duracion_horas":3.5,'
                '"intensidad":7,"estado_emocional":"ansiosa","contexto_adicional":"desde ayer"}'
            )
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
            )

    class FakeChat:
        completions = FakeCompletions()

    class FakeGroq:
        def __init__(self, api_key: str):
            self.api_key = api_key
            self.chat = FakeChat()

    mocker.patch.object(extraccion_llm, "AsyncGroq", FakeGroq)

    result = await extraccion_llm.extraer_datos("Tengo dolor de cabeza")

    assert result["sintomas_madre"] == ["dolor de cabeza"]
    assert result["duracion_horas"] == 3.5
    assert result["intensidad"] == 7
    assert result["estado_emocional"] == "ansiosa"


@pytest.mark.asyncio
async def test_extraer_datos_json_invalido_devuelve_default(mocker):
    """Si Groq devuelve JSON inválido, retorna dict vacío sin excepción."""

    class FakeCompletions:
        async def create(self, **_kwargs):
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content="respuesta no-json"))]
            )

    class FakeChat:
        completions = FakeCompletions()

    class FakeGroq:
        def __init__(self, api_key: str):
            self.api_key = api_key
            self.chat = FakeChat()

    mocker.patch.object(extraccion_llm, "AsyncGroq", FakeGroq)

    result = await extraccion_llm.extraer_datos("Texto ambiguo")

    assert result == {
        "sintomas_madre": [],
        "sintomas_bebe": [],
        "duracion_horas": None,
        "intensidad": None,
        "estado_emocional": None,
        "contexto_adicional": "",
    }
