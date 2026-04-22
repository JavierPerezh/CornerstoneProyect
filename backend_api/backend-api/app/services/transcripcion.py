"""Servicio de transcripción de audio a texto."""

import asyncio
import logging
import os
from pathlib import Path
from time import perf_counter
from uuid import uuid4


logger = logging.getLogger(__name__)


def _transcribe_with_whisper(audio_path: str) -> str:
	"""Ejecuta la transcripción en un hilo para no bloquear el event loop."""

	try:
		from whisper_ctranslate2 import WhisperModel
	except Exception as exc:
		logging.error("No se pudo importar whisper-ctranslate2: %s", exc, exc_info=True)
		raise RuntimeError("Error al inicializar whisper-ctranslate2") from exc

	try:
		model = WhisperModel("medium")
		segments, _info = model.transcribe(audio_path, language="es")
	except Exception as exc:
		logging.error("Error interno de whisper al transcribir '%s': %s", audio_path, exc, exc_info=True)
		raise RuntimeError("Error en el motor de transcripción") from exc

	text_parts: list[str] = []
	for segment in segments:
		segment_text = getattr(segment, "text", "")
		if segment_text:
			text_parts.append(segment_text)

	return " ".join(text_parts).strip()


async def transcribir_audio(audio_path: str) -> str:
	"""Transcribe un archivo WAV y elimina el temporal al finalizar."""

	start = perf_counter()
	logger.debug("Iniciando transcripción de audio: %s", audio_path)

	try:
		if not os.path.exists(audio_path):
			logger.error("Archivo de audio no encontrado: %s", audio_path)
			raise FileNotFoundError(f"No existe el archivo de audio: {audio_path}")

		transcribed_text = await asyncio.to_thread(_transcribe_with_whisper, audio_path)
		cleaned_text = transcribed_text.strip()

		# Heurística simple para detectar audio sin contenido útil.
		if not cleaned_text or not any(char.isalnum() for char in cleaned_text):
			logger.debug("La transcripción está vacía o sin contenido útil: '%s'", cleaned_text)
			raise ValueError("Audio sin contenido")

		elapsed = perf_counter() - start
		logger.debug("Transcripción completada en %.3f segundos", elapsed)
		return cleaned_text

	except FileNotFoundError:
		logging.error("No se pudo transcribir porque el archivo no existe: %s", audio_path, exc_info=True)
		raise
	except ValueError:
		logging.error("Audio inválido o sin contenido en: %s", audio_path, exc_info=True)
		raise
	except Exception as exc:
		logging.error("Error inesperado durante transcripción de '%s': %s", audio_path, exc, exc_info=True)
		raise
	finally:
		try:
			if os.path.exists(audio_path):
				os.remove(audio_path)
				logger.debug("Archivo temporal eliminado: %s", audio_path)
		except Exception as exc:
			logger.exception("No se pudo eliminar el archivo temporal '%s': %s", audio_path, exc)


async def guardar_audio_temporal(audio_bytes: bytes, extension: str = "wav") -> str:
	"""Guarda bytes de audio en /tmp/ con nombre UUID y retorna la ruta absoluta."""

	temp_dir = Path("/tmp")
	temp_dir.mkdir(parents=True, exist_ok=True)

	safe_extension = extension.lstrip(".").strip() or "wav"
	filename = f"{uuid4()}.{safe_extension}"
	file_path = temp_dir / filename

	await asyncio.to_thread(file_path.write_bytes, audio_bytes)
	absolute_path = str(file_path.resolve())
	logger.debug("Audio temporal guardado en: %s", absolute_path)
	return absolute_path
