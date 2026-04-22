"""Servicio de extracción estructurada usando Groq."""

import asyncio
import json
import logging

from groq import AsyncGroq

from app.core.config import get_settings


logger = logging.getLogger(__name__)


def _default_extracted_data() -> dict:
	"""Retorna el payload vacío con el esquema esperado."""

	return {
		"sintomas_madre": [],
		"sintomas_bebe": [],
		"duracion_horas": None,
		"intensidad": None,
		"estado_emocional": None,
		"contexto_adicional": "",
	}


def _clean_json_response(raw_content: str) -> str:
	"""Limpia respuesta del modelo para dejar solo el bloque JSON."""

	cleaned = raw_content.strip()
	cleaned = cleaned.replace("```json", "").replace("```", "").strip()

	start = cleaned.find("{")
	end = cleaned.rfind("}")
	if start != -1 and end != -1 and end > start:
		return cleaned[start : end + 1]

	return cleaned


def _normalize_extracted_data(data: dict) -> dict:
	"""Normaliza y garantiza los campos exactos del esquema de salida."""

	normalized = _default_extracted_data()

	sintomas_madre = data.get("sintomas_madre", [])
	sintomas_bebe = data.get("sintomas_bebe", [])
	normalized["sintomas_madre"] = sintomas_madre if isinstance(sintomas_madre, list) else []
	normalized["sintomas_bebe"] = sintomas_bebe if isinstance(sintomas_bebe, list) else []

	duracion_horas = data.get("duracion_horas")
	normalized["duracion_horas"] = (
		float(duracion_horas) if isinstance(duracion_horas, (int, float)) else None
	)

	intensidad = data.get("intensidad")
	normalized["intensidad"] = int(intensidad) if isinstance(intensidad, (int, float)) else None

	estado_emocional = data.get("estado_emocional")
	normalized["estado_emocional"] = (
		str(estado_emocional) if isinstance(estado_emocional, str) and estado_emocional.strip() else None
	)

	contexto_adicional = data.get("contexto_adicional", "")
	normalized["contexto_adicional"] = (
		str(contexto_adicional) if isinstance(contexto_adicional, str) else ""
	)

	return normalized


async def extraer_datos(texto_usuario: str) -> dict:
	"""Extrae variables clínicas y contexto desde texto libre del usuario."""

	settings = get_settings()
	client = AsyncGroq(api_key=settings.GROQ_API_KEY)

	system_prompt = (
		"Eres un extractor de datos clínicos postparto. "
		"Debes responder SOLO con JSON válido, sin texto adicional, "
		"sin backticks, sin markdown."
	)

	user_prompt = (
		"Extrae los datos del siguiente texto del usuario y devuelve exactamente este JSON: \n"
		"{\n"
		'  "sintomas_madre": ["string"],\n'
		'  "sintomas_bebe": ["string"],\n'
		'  "duracion_horas": float or null,\n'
		'  "intensidad": int or null,\n'
		'  "estado_emocional": string or null,\n'
		'  "contexto_adicional": string\n'
		"}\n\n"
		f"Texto usuario: {texto_usuario}"
	)

	try:
		logger.debug("Solicitando extracción de datos a Groq")
		completion = await asyncio.wait_for(
			client.chat.completions.create(
				model="llama3-70b-8192",
				messages=[
					{"role": "system", "content": system_prompt},
					{"role": "user", "content": user_prompt},
				],
				temperature=0,
			),
			timeout=10,
		)

		content = completion.choices[0].message.content or ""

		# Intento 1: parse directo.
		try:
			parsed = json.loads(content)
			extracted = _normalize_extracted_data(parsed)
			logger.debug("Datos extraídos: %s", extracted)
			return extracted
		except json.JSONDecodeError:
			logger.debug("Primer parseo JSON falló, intentando limpiar respuesta")

		# Intento 2: limpiar y parsear nuevamente.
		try:
			cleaned = _clean_json_response(content)
			parsed = json.loads(cleaned)
			extracted = _normalize_extracted_data(parsed)
			logger.debug("Datos extraídos tras limpieza: %s", extracted)
			return extracted
		except json.JSONDecodeError as exc:
			logger.error(
				"No se pudo parsear JSON de Groq tras 2 intentos. texto_usuario='%s' error='%s' respuesta='%s'",
				texto_usuario,
				exc,
				content,
			)
			return _default_extracted_data()

	except TimeoutError as exc:
		logger.error(
			"Timeout (10s) en extracción con Groq para texto_usuario='%s': %s",
			texto_usuario,
			exc,
		)
		return _default_extracted_data()
	except Exception as exc:
		logger.exception(
			"Error en extracción con Groq para texto_usuario='%s': %s",
			texto_usuario,
			exc,
		)
		return _default_extracted_data()
