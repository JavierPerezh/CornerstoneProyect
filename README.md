# Acompañante Posparto - Dispositivo de Apoyo Emocional y Clínico

## 📖 Descripción del Proyecto

Este proyecto consiste en el desarrollo de un dispositivo físico con forma de animal (oso, pollo o conejo) diseñado para acompañar a madres durante su proceso de posparto. El dispositivo escucha las preguntas o comentarios de la madre, procesa la información mediante inteligencia artificial y reglas clínicas verificables, y responde con mensajes de apoyo empático y recomendaciones basadas en evidencia médica.

El sistema cuenta con una arquitectura modular que incluye:
- Un dispositivo físico con micrófono, altavoz y botón de activación.
- Un backend en Python con FastAPI que orquesta la transcripción de voz (Whisper), extracción de datos con LLM (Groq / Ollama), aplicación de reglas clínicas, generación de respuestas empáticas y conversión de texto a voz (TTS).
- Una base de datos PostgreSQL que almacena anonimizadas las interacciones y permite consultar el historial y el progreso.
- Una aplicación web en React que ofrece un chat de texto y un panel de control con gráficos de evolución.

El objetivo es proporcionar un acompañamiento continuo, confiable y cálido, reduciendo la ansiedad y ayudando a detectar oportunamente signos de alarma como mastitis, depresión posparto o cólicos del lactante.

---

## 🧩 Organización del Proyecto

El proyecto está organizado en un repositorio de GitHub con la siguiente estructura de directorios y archivos principales:

## 📁 Organización del Proyecto

- **`proyecto-posparto/`**
  - **`hardware-firmware/`** - Código para Raspberry Pi 4
    - **`src/`**
      - `main.py` - Programa principal en Python
      - `audio_input.py` - Captura de audio con INMP441
      - `audio_output.py` - Reproducción con PCM5102A + LM386
      - `button.py` - Manejo del botón de grabación
      - `network.py` - Conexión WiFi y envío HTTP
    - **`docs/`**
      - `conexiones.md` - Diagrama de pines y cableado
      - `calibracion.md` - Ajustes de volumen y ganancia
    - `requirements.txt` - Librerías Python para Raspberry Pi
    - `README.md`

  - **`backend-api/`** - Backend principal (FastAPI)
    - **`app/`**
      - `main.py` - Punto de entrada FastAPI
      - **`api/v1/`**
        - **`endpoints/`**
          - `voz.py` - Endpoint para recibir audio
          - `chat.py` - Endpoint para chat web
          - `historial.py` - Endpoint para consultar datos
        - **`models/`**
          - `requests.py` - Modelos Pydantic para peticiones
          - `responses.py` - Modelos Pydantic para respuestas
      - **`core/`**
        - `config.py` - Variables de entorno
        - `database.py` - Conexión a PostgreSQL
      - **`services/`**
        - `transcripcion.py` - Whisper (audio a texto)
        - `extraccion_llm.py` - Extracción de datos con LLM
        - `motor_reglas.py` - Motor determinista de reglas clínicas
        - `regresion_logistica.py` - Modelo de regresión logística para estimación de riesgo
        - `respuesta_empatica.py` - Generación de respuesta cálida con LLM
        - `tts.py` - Text‑to‑Speech (Google Cloud / Coqui)
        - `database.py` - Operaciones con BD (guardar, consultar)
      - **`models/`** (Modelos de machine learning)
        - **`ml/`**
          - `modelo_regresion.pkl` - Modelo entrenado de regresión logística
          - `scaler.pkl` - Escalador para normalizar variables
          - `feature_columns.pkl` - Nombres de las características utilizadas
      - **`training/`**
        - `entrenar_modelo.py` - Script para entrenar el modelo con datos históricos
        - `generar_datos_sinteticos.py` - Generación de datos para entrenamiento
        - `validacion_modelo.py` - Validación cruzada y métricas de rendimiento
    - **`tests/`** - Pruebas unitarias e integración
      - `test_motor_reglas.py`
      - `test_regresion_logistica.py`
      - `test_respuesta_empatica.py`
      - `test_tts.py`
    - **`static/audio/`** - Archivos de audio generados (TTS)
    - **`docs/`**
      - `reglas_clinicas.md` - Documentación de las reglas médicas
      - `modelo_riesgo.md` - Documentación del modelo de regresión logística
      - `contrato_api.md` - Contrato entre frontend y backend
    - `.env.example` - Plantilla de variables de entorno
    - `requirements.txt` - Dependencias Python
    - `README.md`

  - **`database-migrations/`** - Scripts SQL para PostgreSQL
    - **`migrations/`**
      - `001_create_tables.sql`
      - `002_add_indexes.sql`
      - `003_seed_test_data.sql`
      - `004_add_riesgo_column.sql` - Columna para guardar puntuación de riesgo
    - **`queries/`** - Consultas útiles (historial, gráficos)
    - **`docs/`**
      - `SCHEMA.md` - Descripción del modelo de datos
    - `README.md`

  - **`frontend-web/`** - Aplicación React
    - **`public/`**
      - `index.html`
    - **`src/`**
      - `App.jsx` - Componente raíz
      - `main.jsx` - Punto de entrada
      - **`components/`**
        - **`Chat/`**
          - `ChatBox.jsx`
          - `MessageList.jsx`
        - **`Dashboard/`**
          - `Historial.jsx`
          - `Graficos.jsx`
          - `RiesgoCard.jsx` - Tarjeta para mostrar puntuación de riesgo
        - **`Layout/`**
          - `Header.jsx`
          - `Footer.jsx`
      - **`pages/`**
        - `ChatPage.jsx`
        - `ProgresoPage.jsx`
      - **`services/`**
        - `api.js` - Cliente para llamar al backend
      - **`styles/`**
        - `index.css`
    - `.env.example`
    - `package.json`
    - `README.md`

  - `README.md` - Documentación principal del proyecto

---

## 👥 Roles y Responsabilidades por Persona

### 🧸 Jacobo Rincón – Hardware (Raspberry Pi + Componentes)

**Responsabilidades principales:**
- Montar y cablear los componentes electrónicos:
  - **INMP441** (micrófono I2S) para capturar la voz.
  - **PCM5102A** (DAC I2S) + **LM386** (amplificador) + altavoz para reproducir respuestas.
  - Botón táctil para iniciar/detener la grabación.
- Configurar la **Raspberry Pi 4 Model B** con sistema operativo (Raspberry Pi OS Lite) y las librerías necesarias.
- Programar el firmware en Python que:
  - Espera la pulsación del botón.
  - Graba audio en formato WAV mientras el botón está presionado.
  - Envía el archivo de audio al backend mediante HTTP POST.
  - Recibe la respuesta con la URL del audio generado y lo reproduce a través del altavoz.
- Diseñar (con ayuda de impresión 3D) y ensamblar la carcasa con forma de animal, integrando todos los componentes de forma segura y estética.

**Archivos clave que generará:**
- `hardware-firmware/src/main.py`
- `hardware-firmware/src/audio_input.py`
- `hardware-firmware/src/audio_output.py`
- `hardware-firmware/src/button.py`
- `hardware-firmware/src/network.py`
- `hardware-firmware/docs/conexiones.md`
- `hardware-firmware/docs/calibracion.md`

---

### 🧠 Juan Zamudio – Backend Principal + Transcripción + Extracción con LLM

**Responsabilidades principales:**
- Desarrollar el servidor **FastAPI** que orquesta todo el flujo.
- Implementar el endpoint `/api/v1/voz` que recibe el audio desde el hardware, lo guarda temporalmente y llama al servicio de transcripción.
- Integrar **Whisper** (whisper‑ctranslate2) para convertir el audio a texto en español.
- Desarrollar el endpoint `/api/v1/chat` para que el frontend envíe mensajes de texto.
- Implementar el servicio de extracción de datos estructurados usando **Groq API** (o **Ollama** local) con un prompt que devuelva JSON con síntomas, duración, intensidad, días postparto, etc.
- Coordinar con Javier Pérez (Persona 3) para definir el contrato de datos (formato de entrada y salida).
- Integrar los servicios de Javier (motor de reglas, respuesta empática, TTS) en el flujo principal.
- Configurar **CORS** y documentar la API con Swagger (automático en FastAPI).
- Asegurar que el backend esté desplegado y accesible para el hardware (vía ngrok o VPS).

**Archivos clave que generará:**
- `backend-api/app/main.py`
- `backend-api/app/api/v1/endpoints/voz.py`
- `backend-api/app/api/v1/endpoints/chat.py`
- `backend-api/app/services/transcripcion.py`
- `backend-api/app/services/extraccion_llm.py`
- `backend-api/app/core/config.py`
- `backend-api/requirements.txt`

---

### 🩺 Javier Pérez – Motor de Reglas + Respuesta Empática + TTS + Regresión Logística

**Responsabilidades principales:**
- Definir e implementar el **motor determinista de reglas clínicas** (`motor_reglas.py`) usando Python puro (if‑else). Las reglas abarcarán:
  - **Emergencias** (palabras clave como “sangrado abundante”, “convulsiones”) → alerta ROJA.
  - **Mastitis** (fiebre + dolor pecho) → rojo si días postparto < 7, amarillo en otro caso.
  - **Depresión posparto** (tristeza, llanto, cansancio persistente >2 semanas) → amarillo.
  - **Cólicos del lactante** (llanto bebé sin otros síntomas) → verde.
  - **Problemas de lactancia** (grietas, dolor al dar pecho) → amarillo o verde según intensidad.
- Definir e implementar el **modelo de regresión logística** (`regresion_logistica.py`) que complemente el motor determinista, proporcionando una **puntación de riesgo continua** basada en multiples variables: Las variables de entrada son:
  - Número de síntomas reportados
  - Duración de los síntomas
  - Intensidad de 0 a 2 (baja, media, alta)
  - Dias postparto
  - Frecuencia de consultas recientes
  - Combinaciones de síntomas especificas. 
- Entrenar el modelo usando (`generar_datos_sinteticos-py`)
- Implementar la **generación de respuesta empática** (`respuesta_empatica.py`) utilizando Groq API o Ollama. El prompt debe combinar la recomendación médica con un tono cálido, adecuado al nivel de alerta.
- Implementar el servicio de **Text‑to‑Speech** (`tts.py`) usando Google Cloud TTS (o Coqui TTS como alternativa) para convertir la respuesta final en un archivo de audio MP3.
- Crear pruebas unitarias para validar cada regla y el comportamiento de los servicios.
- Documentar las reglas clínicas con sus fuentes y justificaciones.

**Archivos clave que generará:**
- `backend-api/app/services/motor_reglas.py`
- `backend-api/app/services/regresion_logistica.py`
- `backend-api/app/services/respuesta_empatica.py`
- `backend-api/app/services/tts.py`
- `backend-api/app/models/ml/modelo_regresion.pkl`
- `backend-api/tests/test_motor_reglas.py`
- `backend-api/tests/test_respuesta_empatica.py`
- `backend-api/tests/test_tts.py`
- `backend-api/docs/reglas_clinicas.md`
- `backend-api/docs/formato_datos.md`


---

### 🗄️ Gabriela Virgüez – Base de Datos + Endpoints de Historial y Progreso

**Responsabilidades principales:**
- Diseñar el esquema de la base de datos **PostgreSQL**:
  - Tabla `usuarios` (uuid, fecha_registro, dispositivo_id)
  - Tabla `interacciones` (usuario_uuid, fecha, texto_usuario, texto_respuesta, variables_extraidas JSONB, sintomas ARRAY, nivel_alerta, recomendaciones, fuente)
  - Índices para búsquedas rápidas (usuario_uuid + fecha, nivel_alerta, etc.)
- Crear scripts de migración versionados (`001_create_tables.sql`, `002_add_indexes.sql`, etc.).
- Generar datos sintéticos realistas para pruebas (al menos 3 usuarios con 20‑50 interacciones simulando diferentes síntomas y alertas).
- Implementar las funciones de acceso a datos en `app/services/database.py` que permitan a Persona 2 guardar interacciones y consultar historial.
- Desarrollar los **endpoints REST** para el frontend:
  - `GET /api/v1/historial?usuario_uuid=xxx&limit=50&offset=0` → lista de conversaciones.
  - `GET /api/v1/progreso/resumen?usuario_uuid=xxx&periodo=semana` → estadísticas agregadas (totales, alertas por nivel).
  - `GET /api/v1/progreso/grafico?usuario_uuid=xxx&agrupacion=dia` → datos para gráficos (labels y series).
- Documentar el esquema y las consultas en `database-migrations/docs/SCHEMA.md`.
- Apoyar a Persona 5 (Manuela) con la estructura de datos exacta que debe consumir el frontend.

**Archivos clave que generará:**
- `database-migrations/migrations/001_create_tables.sql`
- `database-migrations/migrations/002_add_indexes.sql`
- `database-migrations/migrations/003_seed_test_data.sql`
- `database-migrations/queries/historial_usuario.sql`
- `database-migrations/queries/progreso_semanal.sql`
- `backend-api/app/core/database.py` (conjuntamente con Persona 2)
- `backend-api/app/services/database.py`
- `backend-api/app/api/v1/endpoints/historial.py`

---

### 🎨 Manuela Vergara – Frontend Web (React + Tailwind)

**Responsabilidades principales:**
- Crear la aplicación web con **Vite + React** y estilos con **Tailwind CSS**.
- Diseñar e implementar las siguientes páginas:
  - **Chat** → cuadro de texto, burbujas de conversación, indicador de “escribiendo…”, manejo de envío.
  - **Historial** → lista de conversaciones pasadas, filtros por nivel de alerta, expansión para ver detalles completos.
  - **Progreso** → gráficos de barras/líneas con evolución de alertas (verde, amarillo, rojo) usando **Recharts** o **Chart.js**.
- Crear un servicio `api.js` que consuma los endpoints de Persona 2 y Persona 4.
- Implementar **estados de carga** y **manejo de errores** (mostrar mensajes amigables cuando falle la comunicación).
- Desarrollar con enfoque **responsive** (móvil, tablet, escritorio) y accesibilidad básica.
- Trabajar inicialmente con **datos simulados (mocks)** mientras el backend no está listo, y luego migrar a los endpoints reales.
- Coordinar con Persona 4 para conocer la estructura exacta de los datos de historial y progreso.

**Archivos clave que generará:**
- `frontend-web/src/pages/ChatPage.jsx`
- `frontend-web/src/pages/ProgresoPage.jsx`
- `frontend-web/src/components/Chat/ChatBox.jsx`
- `frontend-web/src/components/Dashboard/Historial.jsx`
- `frontend-web/src/components/Dashboard/Graficos.jsx`
- `frontend-web/src/services/api.js`
- `frontend-web/src/App.jsx`
- `frontend-web/package.json`

---

## 🛠️ Hardware Utilizado (Detalle)

| Componente | Función |
|------------|--------|
| **Raspberry Pi 4 Model B** | Computadora central que ejecuta el firmware en Python, maneja la captura de audio, se conecta a WiFi y se comunica con el backend. |
| **INMP441** | Micrófono digital con interfaz I2S, de alta calidad y bajo ruido. Se utiliza para grabar la voz de la mamá cuando presiona el botón. |
| **PCM5102A** | DAC (convertidor digital‑analógico) con entrada I2S. Convierte el audio digital recibido del backend en señal analógica para el amplificador. |
| **LM386** | Amplificador de audio de baja potencia. Eleva la señal del DAC para manejar el altavoz. |
| **Altavoz** (3W – 5W) | Transductor que reproduce la respuesta de voz generada por el TTS, permitiendo que el animal “hable” con la mamá. |
| **Botón táctil** | Interruptor momentáneo que inicia la grabación al presionarse y la detiene al soltarse. Conectado a un GPIO de la Raspberry Pi. |
| **Batería / Fuente de alimentación** | Para que el dispositivo sea portátil (se recomienda una batería portátil USB‑C que pueda alimentar la Raspberry Pi). |

El firmware de la Raspberry Pi se programa en **Python** utilizando librerías como:
- `sounddevice` o `pyaudio` para capturar audio desde el INMP441.
- `requests` para enviar el archivo WAV al backend.
- `pygame` o `simpleaudio` para reproducir el MP3 recibido.
- `RPi.GPIO` para leer el estado del botón.

---

## 🔄 Flujo General de Datos

1. **La mamá presiona el botón** del animal y habla.
2. La **Raspberry Pi** graba el audio mientras el botón está presionado, lo guarda temporalmente como WAV y lo envía mediante HTTP POST al endpoint `/api/v1/voz` del backend.
3. **El backend (FastAPI)** recibe el audio, lo transcribe con Whisper, extrae datos estructurados con un LLM y pasa esa información al motor de reglas.
4. **El motor de reglas** determina el nivel de alerta (verde/amarillo/rojo) y genera una recomendación médica.
5. **El módulo de respuesta empática** construye un prompt con la recomendación y el texto original, y llama a un LLM para obtener una respuesta cálida en lenguaje natural.
6. **El módulo TTS** convierte ese texto en un archivo de audio MP3 y lo guarda en `static/audio/`.
7. El backend guarda toda la interacción en **PostgreSQL** (texto original, texto respuesta, variables extraídas, alertas, etc.).
8. El backend responde al hardware con un JSON que contiene la URL del audio generado.
9. La **Raspberry Pi** descarga el audio y lo reproduce a través del altavoz (DAC + amplificador).
10. De forma paralela, la mamá puede acceder al **frontend web**, donde ve el historial de todas sus conversaciones y gráficos con la evolución de su estado.

---

*Este proyecto busca demostrar cómo la tecnología puede humanizarse para ofrecer compañía real, empática y clínicamente responsable en una de las etapas más importantes de la vida de una madre y su bebé.*