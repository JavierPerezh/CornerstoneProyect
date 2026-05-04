"""Puente de integración con los servicios backModels de Javier."""

from __future__ import annotations

import asyncio
import json
import logging
import math
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from groq import AsyncGroq
from fastapi import HTTPException, status

from app.core.config import get_settings


logger = logging.getLogger(__name__)

FEATURE_ORDER = [
    "dias_posparto",
    "horas_sueno",
    "nivel_dolor",
    "fiebre_madre",
    "fiebre_bebe",
    "sangrado_abundante",
    "estado_animo",
    "apoyo_social",
    "dificultad_lactancia",
    "llanto_bebe",
    "dolor_cabecera",
    "hinchazon_edema",
    "nivel_ansiedad",
    "actividad_fisica",
    "perdida_apetito",
    "vinculo_bebe",
    "tipo_parto",
]

FEATURE_MEANS = np.array([
    21.636,
    5.96995,
    5.0335,
    0.0495,
    0.044,
    0.018,
    3.008,
    0.802,
    0.2935,
    3.031,
    2.515,
    0.1025,
    3.052,
    0.7,
    0.1065,
    3.5125,
    0.4985,
], dtype=float)

FEATURE_STDS = np.array([
    11.899727055693337,
    1.497685546935671,
    3.121598588864366,
    0.21690954335851617,
    0.20509509989270833,
    0.132951118836962,
    1.3870602005680934,
    0.3984921580156879,
    0.45536551252812285,
    1.4296989193533023,
    1.7169085590094775,
    0.3033047147671793,
    1.424533607887157,
    0.45825756949558394,
    0.30847649829444057,
    1.1094339773055448,
    0.4999977499949375,
], dtype=float)

LABELS = {0: "verde", 1: "amarillo", 2: "rojo"}
LABEL_TO_INDEX = {"verde": 0, "amarillo": 1, "rojo": 2}


@dataclass
class LogisticModel:
    """Modelo de regresión logística multinomial cargado desde JSON."""

    W: np.ndarray
    b: np.ndarray

    @classmethod
    def from_json(cls, payload: dict[str, Any]) -> "LogisticModel":
        return cls(W=np.array(payload["W"], dtype=float), b=np.array(payload["b"], dtype=float))

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        z = np.dot(X, self.W) + self.b
        exp_z = np.exp(z - np.max(z, axis=1, keepdims=True))
        return exp_z / np.sum(exp_z, axis=1, keepdims=True)


class MotorReglasClinicas:
    """Reglas clínicas críticas alineadas con el motor de Javier."""

    def __init__(self) -> None:
        self.UMBRAL_FIEBRE = 38.0
        self.UMBRAL_DOLOR_CRITICO = 8

    def evaluar_estado(self, datos: dict[str, Any]) -> tuple[str, str]:
        if datos.get("sangrado_abundante") == 1:
            return "rojo", "Busca ayuda médica inmediata. El sangrado abundante puede ser una emergencia."
        if datos.get("dolor_cabecera", 0) >= 8 and datos.get("hinchazon_edema") == 1:
            return "rojo", "Alerta de preeclampsia: Dolor de cabeza intenso con hinchazón. Ve a urgencias."
        if datos.get("fiebre_madre", 0) >= self.UMBRAL_FIEBRE:
            return "rojo", "Fiebre alta detectada. Podría ser una infección; contacta a tu médico ahora."
        if datos.get("fiebre_bebe") == 1:
            return "rojo", "La fiebre en un recién nacido requiere evaluación pediátrica urgente."
        if datos.get("estado_animo", 0) == 0 and datos.get("nivel_ansiedad", 0) >= 9:
            return "rojo", "Tu bienestar emocional es prioridad. Por favor, contacta a una línea de apoyo o profesional hoy mismo."
        if datos.get("dificultad_lactancia") == 1 and datos.get("nivel_dolor") >= 6:
            return "amarillo", "El dolor persistente en el pecho puede ser inicio de mastitis. Consulta con tu asesora de lactancia."
        if datos.get("dolor_herida", 0) >= 6 or datos.get("secrecion_herida", 0) == 1:
            return "amarillo", "Revisa tu herida quirúrgica. Si hay enrojecimiento o secreción, consulta a tu médico."
        if datos.get("dias_sin_evacuar", 0) >= 4:
            return "amarillo", "Aumenta la hidratación y fibra. Si el malestar persiste, contacta a tu médico."
        if datos.get("horas_sueno", 8) <= 3:
            return "amarillo", "El agotamiento extremo afecta tu salud. Intenta delegar tareas para descansar al menos 4 horas seguidas."
        if datos.get("dificultad_lactancia") == 1 and datos.get("nivel_dolor") < 4:
            return "verde", "La lactancia es un proceso de aprendizaje. Estás haciendo un gran trabajo, ten paciencia."
        if datos.get("dias_posparto", 0) <= 10 and datos.get("estado_animo") == 2:
            return "verde", "Es normal sentir sensibilidad estos días. Se llama Baby Blues y suele pasar pronto."
        if datos.get("vinculo_bebe", 0) >= 4:
            return "verde", "Me alegra saber que te sientes conectada con tu bebé. Ese vínculo es maravilloso."
        if datos.get("actividad_fisica") == 0 and datos.get("dias_posparto", 0) > 15:
            return "verde", "Cuando te sientas lista, caminar 10 minutos puede ayudarte a mejorar tu ánimo."
        if datos.get("perdida_apetito") == 1:
            return "verde", "Recuerda alimentarte bien para recuperar energías. Pequeñas comidas frecuentes pueden ayudar."
        return "verde", "Todo parece estar dentro de lo esperado. Sigue descansando y disfrutando de tu bebé."


class _FeatureMapper:
    """Convierte la extracción libre del LLM al vector de 17 features de Javier."""

    _DEFAULTS = {name: float(mean) for name, mean in zip(FEATURE_ORDER, FEATURE_MEANS)}

    @staticmethod
    def _text_sources(extracted: dict[str, Any]) -> str:
        parts = [
            str(extracted.get("contexto_adicional") or ""),
            " ".join(extracted.get("sintomas_madre") or []),
            " ".join(extracted.get("sintomas_bebe") or []),
        ]
        return " ".join(parts).lower()

    @staticmethod
    def _contains_any(text: str, keywords: list[str]) -> bool:
        return any(keyword in text for keyword in keywords)

    @staticmethod
    def _parse_number(text: str, pattern: str) -> float | None:
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            return None
        value = match.group(1).replace(",", ".")
        try:
            return float(value)
        except ValueError:
            return None

    def map(self, extracted: dict[str, Any]) -> dict[str, float]:
        text = self._text_sources(extracted)
        mapped = dict(self._DEFAULTS)

        dias = self._parse_number(text, r"(\d+(?:[\.,]\d+)?)\s*(?:d[ií]as?|dias)\s*(?:posparto|postparto)")
        if dias is not None:
            mapped["dias_posparto"] = dias

        horas = self._parse_number(text, r"(\d+(?:[\.,]\d+)?)\s*(?:horas?|h)\s*(?:de\s*)?(?:sueño|sueno|descanso)")
        if horas is not None:
            mapped["horas_sueno"] = horas
        elif extracted.get("duracion_horas") is not None:
            try:
                mapped["horas_sueno"] = float(extracted["duracion_horas"])
            except (TypeError, ValueError):
                pass

        intensidad = extracted.get("intensidad")
        if isinstance(intensidad, (int, float)):
            mapped["nivel_dolor"] = float(max(0, min(10, intensidad)))

        if self._contains_any(text, ["fiebre", "temperatura alta", "caliente"]):
            mapped["fiebre_madre"] = 38.0 if self._contains_any(text, ["fiebre", "temperatura alta"]) else 37.5
        if self._contains_any(text, ["bebé con fiebre", "bebe con fiebre", "fiebre del bebé", "fiebre del bebe"]):
            mapped["fiebre_bebe"] = 1.0
        if self._contains_any(text, ["sangrado", "hemorragia", "sangra mucho", "abundante"]):
            mapped["sangrado_abundante"] = 1.0

        emotional = str(extracted.get("estado_emocional") or "").lower()
        if emotional in {"ansiosa", "muy ansiosa", "nerviosa"}:
            mapped["estado_animo"] = 1.0
            mapped["nivel_ansiedad"] = 8.0
        elif emotional in {"triste", "deprimida", "llorosa"}:
            mapped["estado_animo"] = 1.5
            mapped["nivel_ansiedad"] = 5.0
        elif emotional in {"tranquila", "bien", "contenta", "feliz"}:
            mapped["estado_animo"] = 4.5
            mapped["nivel_ansiedad"] = 1.5

        if self._contains_any(text, ["sola", "sin apoyo", "nadie me ayuda", "no tengo apoyo"]):
            mapped["apoyo_social"] = 0.0
        elif self._contains_any(text, ["mi pareja", "mi familia", "me ayudan", "apoyo"]):
            mapped["apoyo_social"] = 1.0

        if self._contains_any(text, ["lactancia", "amamantar", "pecho", "seno", "senos"]):
            mapped["dificultad_lactancia"] = 1.0
        if self._contains_any(text, ["llora mucho", "llanto", "inconsolable", "muy irritable"]):
            mapped["llanto_bebe"] = 5.0
        if self._contains_any(text, ["dolor de cabeza", "cefalea", "migraña", "migraña"]):
            mapped["dolor_cabecera"] = 8.0 if self._contains_any(text, ["fuerte", "intenso"]) else 5.0
        if self._contains_any(text, ["hinchazón", "edema", "piernas hinchadas"]):
            mapped["hinchazon_edema"] = 1.0
        if self._contains_any(text, ["caminé", "camine", "ejercicio", "actividad física", "actividad fisica"]):
            mapped["actividad_fisica"] = 1.0
        if self._contains_any(text, ["sin apetito", "no tengo hambre", "poco apetito", "perdí el apetito"]):
            mapped["perdida_apetito"] = 1.0
        if self._contains_any(text, ["me siento conectada", "me siento conectada", "vínculo", "vinculo", "amor con mi bebé", "amor con mi bebe"]):
            mapped["vinculo_bebe"] = 5.0
        if self._contains_any(text, ["cesárea", "cesarea"]):
            mapped["tipo_parto"] = 1.0
        elif self._contains_any(text, ["parto vaginal", "vaginal"]):
            mapped["tipo_parto"] = 0.0

        return mapped


class JavierRiskServiceAdapter:
    """Calcula el riesgo como en el stack de Javier, pero adaptado al backend actual."""

    def __init__(self, model_path: Path | None = None) -> None:
        self.model_path = model_path or Path(__file__).resolve().parents[1] / "models" / "weights" / "parametros_finales.json"
        self.feature_order = FEATURE_ORDER
        self.preprocessor_mean = FEATURE_MEANS
        self.preprocessor_std = FEATURE_STDS.copy()
        self.preprocessor_std[self.preprocessor_std == 0] = 1.0
        self.model = self._load_model()
        self.motor_reglas = MotorReglasClinicas()
        self.mapper = _FeatureMapper()

    def _load_model(self) -> LogisticModel:
        if not self.model_path.exists():
            logger.warning("No se encontró el archivo de pesos en %s. Se usará un modelo base.", self.model_path)
            zeros = np.zeros((len(FEATURE_ORDER), 3), dtype=float)
            return LogisticModel(W=zeros, b=np.zeros((1, 3), dtype=float))

        with self.model_path.open("r", encoding="utf-8") as handle:
            config = json.load(handle)
        return LogisticModel.from_json(config["model_params"])

    def _scale(self, X: np.ndarray) -> np.ndarray:
        return (X - self.preprocessor_mean) / self.preprocessor_std

    def _class_to_alerta(self, index: int) -> str:
        return LABELS.get(index, "verde")

    def procesar_evaluacion_completa(self, datos_madre_dict: dict[str, Any]) -> dict[str, Any]:
        mapped = self.mapper.map(datos_madre_dict)
        alerta_reglas, recomendacion_reglas = self.motor_reglas.evaluar_estado(mapped)

        vector = np.array([[mapped[feature] for feature in self.feature_order]], dtype=float)
        scaled = self._scale(vector)
        probabilities = self.model.predict_proba(scaled)[0]
        pred_index = int(np.argmax(probabilities))
        alerta_ml = self._class_to_alerta(pred_index)
        confianza_ml = float(probabilities[pred_index])
        jerarquia = {"verde": 0, "amarillo": 1, "rojo": 2}

        if jerarquia[alerta_reglas] >= jerarquia.get(alerta_ml, 0):
            nivel_final = alerta_reglas
            metodo = "Reglas Clinicas (Prioridad Seguridad)"
        else:
            nivel_final = alerta_ml
            metodo = "Modelo IA (Tendencia Estadistica)"

        score_ml = float(confianza_ml)
        return {
            "nivel_riesgo": nivel_final,
            "nivel_alerta": nivel_final,
            "puntuacion_riesgo": score_ml,
            "recomendacion_base": recomendacion_reglas,
            "recomendaciones": recomendacion_reglas,
            "fuente": "javier_risk_service",
            "requiere_accion_inmediata": nivel_final == "rojo",
            "reglas_activadas": [],
            "detalle_tecnico": {
                "metodo_decisivo": metodo,
                "score_ml": score_ml,
                "confianza_ml": score_ml,
                "alerta_ml": alerta_ml,
                "alerta_reglas": alerta_reglas,
            },
        }

    async def predecir(self, datos_madre_dict: dict[str, Any]) -> dict[str, Any]:
        return await asyncio.to_thread(self.procesar_evaluacion_completa, datos_madre_dict)


class JavierMotorReglasAdapter:
    """Adaptador asíncrono para el motor de reglas de Javier."""

    def __init__(self) -> None:
        self.motor = MotorReglasClinicas()
        self.mapper = _FeatureMapper()

    def evaluar_estado(self, datos: dict[str, Any]) -> tuple[str, str]:
        mapped = self.mapper.map(datos)
        return self.motor.evaluar_estado(mapped)

    async def evaluar(self, datos: dict[str, Any]) -> dict[str, Any]:
        alerta, recomendacion = await asyncio.to_thread(self.evaluar_estado, datos)
        return {
            "nivel_alerta": alerta,
            "requiere_accion_inmediata": alerta == "rojo",
            "recomendaciones": recomendacion,
            "fuente": "javier_motor_reglas",
            "reglas_activadas": [],
        }


class JavierRespuestaEmpaticaAdapter:
    """Genera una respuesta empática con Groq y fallback local."""

    def __init__(self) -> None:
        self.model = "llama-3.3-70b-versatile"
        self._client: AsyncGroq | None = None

    def _get_client(self) -> AsyncGroq:
        if self._client is None:
            settings = get_settings()
            self._client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        return self._client

    async def generar_respuesta(
        self,
        texto_usuario: str,
        nivel_alerta: str,
        recomendacion_medica: str,
        puntuacion_riesgo: float,
    ) -> str:
        system_prompt = (
            "Eres un acompanante de posparto empatico y experto. Tu objetivo es validar "
            "las emociones de la madre y dar instrucciones claras basadas en medicina. "
            "Reglas estrictas:\n"
            "1. Idioma: Espanol.\n"
            "2. Extension: Maximo 280 caracteres.\n"
            "3. Tono: Calido, calmado y sin juicios.\n"
            "4. Estructura: Valida la emocion, explica brevemente el riesgo y da el paso a seguir."
        )
        prompt_usuario = (
            f"Contexto de la madre: '{texto_usuario}'\n"
            f"Evaluacion tecnica: Nivel de alerta {nivel_alerta.upper()}.\n"
            f"Puntuacion de riesgo logistico: {puntuacion_riesgo:.2f}.\n"
            f"Instruccion medica: {recomendacion_medica}\n\n"
            "Genera la respuesta directa para la madre:"
        )

        try:
            completion = await self._get_client().chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt_usuario},
                ],
                model=self.model,
                temperature=0.5,
                max_tokens=150,
            )
            content = completion.choices[0].message.content or ""
            return content.strip() if content.strip() else self._fallback(recomendacion_medica)
        except Exception as exc:
            logging.error("Error en la generacion de respuesta LLM: %s", exc, exc_info=True)
            return self._fallback(recomendacion_medica)

    async def generar(self, **kwargs: Any) -> str:
        texto_usuario = kwargs.get("texto_usuario", "")
        nivel_alerta = kwargs.get("nivel_alerta") or kwargs.get("reglas_resultado", {}).get("nivel_alerta", "verde")
        reglas_resultado = kwargs.get("reglas_resultado", {}) or {}
        riesgo_resultado = kwargs.get("riesgo_resultado", {}) or {}
        recomendacion_medica = reglas_resultado.get("recomendaciones") or reglas_resultado.get("recomendacion_base") or kwargs.get("recomendacion_medica") or "Sigue las indicaciones de tu profesional de salud."
        puntuacion_riesgo = riesgo_resultado.get("puntuacion_riesgo")
        if puntuacion_riesgo is None:
            puntuacion_riesgo = riesgo_resultado.get("detalle_tecnico", {}).get("score_ml", 0.0)
        return await self.generar_respuesta(texto_usuario, str(nivel_alerta), str(recomendacion_medica), float(puntuacion_riesgo or 0.0))

    def _fallback(self, recomendacion_medica: str) -> str:
        return (
            "Entiendo como te sientes. Segun lo que me cuentas, lo mas importante es: "
            f"{recomendacion_medica}. Estoy aqui para acompanarte."
        )


class JavierTTSAdapter:
    """Genera audio MP3 con Edge-TTS o deja el flujo en modo degradado."""

    def __init__(self) -> None:
        self.voice = "es-MX-DaliaNeural"
        self.static_dir = Path(__file__).resolve().parents[1] / "static" / "audio"
        self.static_dir.mkdir(parents=True, exist_ok=True)

    async def _save(self, texto: str) -> str | None:
        try:
            import edge_tts  # type: ignore
        except Exception as exc:
            logging.error("Edge-TTS no está disponible: %s", exc, exc_info=True)
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        identifier = hex(abs(hash(texto)) % (16**8))[2:].zfill(8)
        filename = f"respuesta_{timestamp}_{identifier}.mp3"
        path = self.static_dir / filename
        try:
            communicate = edge_tts.Communicate(texto, self.voice)
            await communicate.save(str(path))
            return f"/static/audio/{filename}"
        except Exception as exc:
            logging.error("Error en Edge-TTS: %s", exc, exc_info=True)
            return None

    async def convertir(self, texto: str) -> dict[str, Any]:
        audio_url = await self._save(texto)
        return {"audio_url": audio_url, "texto_respuesta": texto}

    def generar_audio(self, texto: str) -> str | None:
        try:
            return asyncio.run(self._save(texto))
        except RuntimeError:
            return None


class CleanupService:
    """Limpieza de archivos mp3 antiguos en static/audio."""

    def __init__(self) -> None:
        self.audio_dir = Path(__file__).resolve().parents[1] / "static" / "audio"
        self.dias_retencion = 7
        self.max_archivos = 1000

    def ejecutar_limpieza(self) -> None:
        if not self.audio_dir.exists():
            return

        ahora = datetime.now().timestamp()
        segundos_retencion = self.dias_retencion * 86400
        archivos = list(self.audio_dir.glob("*.mp3"))

        for archivo in archivos:
            try:
                if ahora - archivo.stat().st_mtime > segundos_retencion:
                    archivo.unlink()
            except Exception as exc:
                logging.error("Error al eliminar %s: %s", archivo.name, exc, exc_info=True)

        restantes = sorted(self.audio_dir.glob("*.mp3"), key=lambda item: item.stat().st_mtime)
        exceso = max(0, len(restantes) - self.max_archivos)
        for archivo in restantes[:exceso]:
            try:
                archivo.unlink()
            except Exception as exc:
                logging.error("Error al eliminar por cuota %s: %s", archivo.name, exc, exc_info=True)


@dataclass
class JavierServicesBundle:
    motor_reglas: JavierMotorReglasAdapter
    risk_service: JavierRiskServiceAdapter
    respuesta_empatica: JavierRespuestaEmpaticaAdapter
    tts: JavierTTSAdapter
    cleanup: CleanupService

    def as_dict(self) -> dict[str, Any]:
        return {
            "motor_reglas": self.motor_reglas,
            "risk_service": self.risk_service,
            "respuesta_empatica": self.respuesta_empatica,
            "tts": self.tts,
            "cleanup": self.cleanup,
        }


def build_javier_services() -> dict[str, Any]:
    """Construye el bundle de servicios de Javier para inyectarlo en app.state.services."""

    bundle = JavierServicesBundle(
        motor_reglas=JavierMotorReglasAdapter(),
        risk_service=JavierRiskServiceAdapter(),
        respuesta_empatica=JavierRespuestaEmpaticaAdapter(),
        tts=JavierTTSAdapter(),
        cleanup=CleanupService(),
    )
    return bundle.as_dict()
