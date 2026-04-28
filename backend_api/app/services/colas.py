"""Gestión de tareas en background para el flujo de voz."""

from datetime import datetime, timedelta, timezone
import logging
from time import perf_counter
from threading import Lock
from uuid import uuid4

from fastapi import BackgroundTasks

from app.services.extraccion_llm import extraer_datos
from app.services import database as database_service
from app.services.transcripcion import guardar_audio_temporal, transcribir_audio


logger = logging.getLogger(__name__)

TASK_STORE: dict[str, dict] = {}
TASK_STORE_LOCK = Lock()
TASK_TTL = timedelta(hours=1)


def _now_utc() -> datetime:
	"""Retorna fecha/hora actual con zona horaria UTC."""

	return datetime.now(timezone.utc)


def _step_ms(start: float) -> float:
	"""Calcula duración en milisegundos de un paso."""

	return (perf_counter() - start) * 1000


def _resolve_service(services: dict, key: str):
	"""Obtiene un servicio requerido o lanza un error descriptivo."""

	service = services.get(key)
	if service is None:
		raise KeyError(f"Servicio requerido no encontrado: {key}")
	return service


def _resolve_audio_url(tts_result) -> str | None:
	"""Extrae una URL de audio desde distintos formatos de retorno."""

	if isinstance(tts_result, str):
		return tts_result
	if isinstance(tts_result, dict):
		value = tts_result.get("audio_url") or tts_result.get("url")
		return str(value) if value else None
	return None


def crear_tarea() -> str:
	"""Crea una tarea en estado procesando y retorna su ID."""

	limpiar_tareas_viejas()
	task_id = str(uuid4())
	with TASK_STORE_LOCK:
		TASK_STORE[task_id] = {
			"task_id": task_id,
			"status": "procesando",
			"audio_url": None,
			"texto_respuesta": None,
			"error": None,
			"created_at": _now_utc(),
		}

	logger.debug("Tarea creada: %s", task_id)
	return task_id


def actualizar_tarea(task_id: str, **kwargs) -> None:
	"""Actualiza campos del estado de una tarea existente."""

	with TASK_STORE_LOCK:
		task = TASK_STORE.get(task_id)
		if task is None:
			logger.debug("Intento de actualizar tarea inexistente: %s", task_id)
			return
		task.update(kwargs)

	logger.debug("Tarea %s actualizada con %s", task_id, kwargs)


def obtener_tarea(task_id: str) -> dict | None:
	"""Retorna el estado actual de una tarea o None si no existe."""

	with TASK_STORE_LOCK:
		task = TASK_STORE.get(task_id)
		if task is None:
			return None
		return dict(task)


def limpiar_tareas_viejas() -> None:
	"""Elimina tareas con más de 1 hora de antigüedad."""

	cutoff = _now_utc() - TASK_TTL
	deleted_ids: list[str] = []

	with TASK_STORE_LOCK:
		for task_id, task in list(TASK_STORE.items()):
			created_at = task.get("created_at")
			if isinstance(created_at, datetime) and created_at < cutoff:
				deleted_ids.append(task_id)
				del TASK_STORE[task_id]

	if deleted_ids:
		logger.debug("Tareas eliminadas por antigüedad: %s", deleted_ids)


def encolar_procesamiento_audio(
	background_tasks: BackgroundTasks,
	*,
	audio_bytes: bytes,
	device_id: str,
	db_conn,
	services: dict,
) -> str:
	"""Crea y encola una tarea de procesamiento de audio usando BackgroundTasks."""

	task_id = crear_tarea()
	background_tasks.add_task(
		procesar_audio,
		task_id,
		audio_bytes,
		device_id,
		db_conn,
		services,
	)
	logger.debug("Tarea %s encolada en BackgroundTasks", task_id)
	return task_id


async def procesar_audio(task_id, audio_bytes, device_id, db_conn, services):
	"""Worker principal del flujo de voz ejecutado en background."""

	logger.debug("Inicio de procesamiento para task_id=%s device_id=%s", task_id, device_id)

	try:
		step_start = perf_counter()
		ruta_audio = await guardar_audio_temporal(audio_bytes)
		logger.debug("Paso 1 guardar_audio_temporal completado en %.2f ms", _step_ms(step_start))

		step_start = perf_counter()
		texto_usuario = await transcribir_audio(ruta_audio)
		logger.debug("Paso 2 transcribir_audio completado en %.2f ms", _step_ms(step_start))

		step_start = perf_counter()
		datos_extraidos = await extraer_datos(texto_usuario)
		logger.debug("Paso 3 extraer_datos completado en %.2f ms", _step_ms(step_start))

		motor_reglas = _resolve_service(services, "motor_reglas")
		risk_service = _resolve_service(services, "risk_service")
		respuesta_empatica = _resolve_service(services, "respuesta_empatica")
		tts = _resolve_service(services, "tts")
		step_start = perf_counter()
		reglas_resultado = await motor_reglas.evaluar(datos_extraidos)
		logger.debug("Paso 4 motor_reglas.evaluar completado en %.2f ms", _step_ms(step_start))

		step_start = perf_counter()
		riesgo_resultado = await risk_service.predecir(datos_extraidos)
		logger.debug("Paso 5 risk_service.predecir completado en %.2f ms", _step_ms(step_start))

		step_start = perf_counter()
		respuesta_texto = await respuesta_empatica.generar(
			texto_usuario=texto_usuario,
			datos_extraidos=datos_extraidos,
			reglas_resultado=reglas_resultado,
			riesgo_resultado=riesgo_resultado,
		)
		logger.debug("Paso 6 respuesta_empatica.generar completado en %.2f ms", _step_ms(step_start))

		step_start = perf_counter()
		tts_resultado = await tts.convertir(respuesta_texto)
		logger.debug("Paso 7 tts.convertir completado en %.2f ms", _step_ms(step_start))

		audio_url = _resolve_audio_url(tts_resultado)

		step_start = perf_counter()
		if hasattr(db_conn, "acquire"):
			async with db_conn.acquire() as conn_for_save:
				interaccion = await database_service.guardar_interaccion(
					conn=conn_for_save,
					device_id=device_id,
					origen="voz",
					texto_usuario=texto_usuario,
					texto_respuesta=respuesta_texto,
					datos_extraidos=datos_extraidos,
					reglas_resultado=reglas_resultado,
					riesgo_resultado=riesgo_resultado,
					tts_resultado=tts_resultado,
				)
		else:
			interaccion = await database_service.guardar_interaccion(
				conn=db_conn,
				device_id=device_id,
				origen="voz",
				texto_usuario=texto_usuario,
				texto_respuesta=respuesta_texto,
				datos_extraidos=datos_extraidos,
				reglas_resultado=reglas_resultado,
				riesgo_resultado=riesgo_resultado,
				tts_resultado=tts_resultado,
			)
		logger.debug(
			"Paso 8 database_service.guardar_interaccion completado en %.2f ms",
			_step_ms(step_start),
		)

		interaccion_id = None
		if isinstance(interaccion, dict):
			interaccion_id = interaccion.get("interaccion_id") or interaccion.get("id")

		step_start = perf_counter()
		actualizar_tarea(
			task_id,
			status="listo",
			audio_url=audio_url,
			texto_respuesta=respuesta_texto,
			error=None,
			interaccion_id=interaccion_id,
		)
		logger.debug("Paso 9 actualizar_tarea completado en %.2f ms", _step_ms(step_start))

	except Exception as exc:
		logger.exception("Error procesando tarea %s: %s", task_id, exc)
		actualizar_tarea(task_id, status="error", error=str(exc))
