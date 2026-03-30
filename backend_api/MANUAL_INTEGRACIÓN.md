
# 📘 Manual de Integración: Core Clínico y Servicios de IA 

Este documento detalla cómo integrar los módulos desarrollados por **Javier Pérez** en el flujo principal del backend. Estos servicios orquestan la inteligencia médica, la evaluación probabilística y la síntesis de voz del dispositivo.

---

## 1. Integración del Orquestador de Riesgo (Juan/Backend)
El archivo `app/services/risk_service.py` es el punto de entrada principal. Recibe el diccionario de 17 variables extraídas por el LLM y devuelve el nivel de alerta y la recomendación técnica.

**Ejemplo de uso en el Endpoint:**

```python
from app.services.risk_service import risk_service

# Datos simulados que vienen del extractor LLM
datos_madre = {
    "sangrado_abundante": 0,
    "fiebre_madre": 37.5,
    "dolor_cabecera": 4,
    "estado_animo": 2,
    # ... resto de las 17 variables
}

resultado = risk_service.procesar_evaluacion_completa(datos_madre)

# resultado contendrá:
# {
#   "nivel_riesgo": "amarillo",
#   "recomendacion_base": "Parece que estás pasando un momento difícil...",
#   "detalle_tecnico": { ... }
# }
```

---

## 4. Generación de Respuesta y Audio (Jacobo/Hardware)
Una vez obtenido el riesgo, se debe generar la respuesta empática y el archivo de audio para la Raspberry Pi.

```python
from app.services.respuesta_empatica import respuesta_service
from app.services.tts import tts_service

# 1. Generar texto empático (Llama 3.3 70B)
texto_final = respuesta_service.generar_respuesta(
    texto_usuario="Me siento muy sola hoy",
    nivel_alerta=resultado["nivel_riesgo"],
    recomendacion_medica=resultado["recomendacion_base"],
    puntuacion_riesgo=resultado["detalle_tecnico"]["score_ml"]
)

# 2. Generar audio (Edge-TTS)
url_audio = tts_service.generar_audio(texto_final)
# Devuelve: "/static/audio/respuesta_20260330_abc123.mp3"
```

---

## 5. Mantenimiento de Servidor (Cleanup)
Para evitar que el VPS se llene de archivos MP3, Juan debe programar una tarea de limpieza.

```python
from app.services.cleanup import cleanup_service

# Se recomienda ejecutar esto una vez al día o cada 100 interacciones
cleanup_service.ejecutar_limpieza()
```

---

## 6. Consideraciones Técnicas 
- **Prioridad de Seguridad:** El sistema aplica una lógica de arbitraje. Si el **Motor de Reglas (20 reglas científicas)** detecta un riesgo "Rojo", este prevalecerá sobre el modelo de **Regresión Logística**, garantizando que nunca se ignore una emergencia médica por un error estadístico.
- **Formato de Audio:** Los archivos se guardan en `static/audio/` en formato MP3 optimizado para la reproducción en la Raspberry Pi 4.
- **Pruebas:** Antes de cada despliegue, correr `python3 -m unittest discover tests` para asegurar que la matemática del modelo sigue intacta.

---
**Desarrollado por:** Javier Pérez
**Versión:** 1.0.0
```
