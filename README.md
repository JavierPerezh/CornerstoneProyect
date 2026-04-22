# Acompañante Posparto - Dispositivo de Apoyo Emocional y Clínico

## 📖 Descripción del Proyecto

Este proyecto consiste en el desarrollo de un dispositivo físico con forma de animal (oso, pollo o conejo) diseñado para acompañar a madres durante su proceso de posparto. El dispositivo escucha las preguntas o comentarios de la madre, procesa la información mediante inteligencia artificial y reglas clínicas verificables, y responde con mensajes de apoyo empático y recomendaciones basadas en evidencia médica.

El sistema está diseñado para brindar acompañamiento integral considerando tanto la salud de la madre como la del bebé, analizando síntomas, comportamientos y emociones de ambos para ofrecer una visión holística del bienestar familiar durante el posparto.

El sistema cuenta con una arquitectura modular que incluye:

- Un dispositivo físico con micrófono, altavoz, botón de activación y LED de estado.
- Un backend en Python con FastAPI que orquesta la transcripción de voz (Whisper), extracción de datos con LLM (Groq como proveedor principal), aplicación de reglas clínicas, generación de respuestas empáticas y conversión de texto a voz (TTS).
- Una base de datos PostgreSQL que almacena anonimizadas las interacciones (tanto las realizadas por voz como las escritas en el chat web) y permite consultar el historial y el progreso.
- Una aplicación web en React que ofrece un chat de texto (con la misma inteligencia artificial que el dispositivo), un panel de control con gráficos de evolución de síntomas de la madre y el bebé, y un historial unificado de todas las conversaciones (voz y texto).

El objetivo es proporcionar un acompañamiento continuo, confiable y cálido, reduciendo la ansiedad y ayudando a detectar oportunamente signos de alarma como mastitis, depresión posparto, cólicos del lactante u otras complicaciones tanto en la madre como en el bebé.

---

## 🧩 Organización del Proyecto

El proyecto está organizado en un repositorio de GitHub con la siguiente estructura de directorios y archivos principales:

- **`proyecto-posparto/`**
  - **`hardware-firmware/`** - Código para Raspberry Pi 4
    - **`src/`**
      - `main.py` - Programa principal en Python
      - `audio_input.py` - Captura de audio con INMP441
      - `audio_output.py` - Reproducción con PCM5102A + LM386
      - `button.py` - Manejo del botón de grabación
      - `led.py` - Control del LED de estado
      - `network.py` - Conexión WiFi y envío HTTP
    - **`docs/`**
      - `conexiones.md` - Diagrama de pines y cableado
      - `calibracion.md` - Ajustes de volumen y ganancia
      - `configuracion_i2s.md` - Pasos para habilitar I2S en Raspberry Pi OS
    - `requirements.txt` - Librerías Python para Raspberry Pi
    - `README.md`

  - **`backend-api/`** - Backend principal (FastAPI)
    - **`app/`**
      - `main.py` - Punto de entrada FastAPI
      - **`api/v1/`**
        - **`endpoints/`**
          - `voz.py` - Endpoint para recibir audio desde el hardware
          - `chat.py` - Endpoint para mensajes de texto desde el frontend
          - `historial.py` - Endpoint para consultar historial y progreso
          - `auth.py` - Endpoints para autenticación (código de dispositivo)
        - **`models/`**
          - `requests.py` - Modelos Pydantic para peticiones
          - `responses.py` - Modelos Pydantic para respuestas
      - **`core/`**
        - `config.py` - Variables de entorno
        - `database.py` - Conexión a PostgreSQL
        - `security.py` - Funciones de autenticación y API keys
        - `math_models.py` - Modelo regresión logística
        - `preprocessing.py` - Codificación one hot manual
      - **`services/`**
        - `transcripcion.py` - Whisper (audio a texto)
        - `extraccion_llm.py` - Extracción de datos con LLM (Groq)
        - `motor_reglas.py` - Motor determinista de reglas clínicas
        - `risk_service` - Analizador entre regresión y reglas
        - `respuesta_empatica.py` - Generación de respuesta cálida con LLM (Groq)
        - `tts.py` - Text‑to‑Speech (Google Cloud / Coqui)
        - `database.py` - Operaciones con BD (guardar, consultar)
        - `cleanup.py` - Limpieza automática de archivos de audio temporales
        - `colas.py` - Sistema de colas para procesamiento asíncrono (Celery o background tasks)
      - **`models/`** (Modelos de machine learning)
        - `schema`
        - **`weights`**
          - `Parametros Finales` - Modelo de regresión ya entrenado 
      - **`training/`**
        - `gradient_decent.py` - Script para entrenar el modelo con datos históricos
        - `generar_datos_sinteticos.py` - Generación de datos para entrenamiento
    - **`tests/`** - Pruebas unitarias e integración
      - `test_math.py`
      - `test_preprocessing.py`
      - `test_ai_services.py`
      - `test_endpoints.py`
    - **`static/audio/`** - Archivos de audio generados (TTS)
    - **`docs/`**
      - `reglas_clinicas.md` - Documentación de las reglas médicas
      - `modelo_riesgo.md` - Documentación del modelo de regresión logística
      - `contrato_api.md` - Contrato entre frontend y backend
    - `run_tests.py`
    - `.env.example` - Plantilla de variables de entorno
    - `requirements.txt` - Dependencias Python
    - `README.md`

  - **`database-migrations/`** - Scripts SQL para PostgreSQL
    - **`migrations/`**
      - `001_create_tables.sql`
      - `002_add_indexes.sql`
      - `003_seed_test_data.sql`
      - `004_add_anonimizacion.sql`
    - **`queries/`** - Consultas útiles (historial, gráficos)
    - **`docs/`**
      - `SCHEMA.md` - Descripción detallada del modelo de datos
    - `README.md`

  - **`frontend-web/`** - Aplicación React
    - **`public/`**
      - `index.html`
    - **`src/`**
      - `App.jsx` - Componente raíz
      - `main.jsx` - Punto de entrada
      - **`components/`**
        - **`Chat/`**
          - `ChatBox.jsx` - Área de chat unificada (muestra mensajes de voz y texto)
          - `MessageList.jsx` - Lista de mensajes con indicador de origen (voz o texto)
          - `InputArea.jsx` - Campo de texto y botón de envío
        - **`Dashboard/`**
          - `Historial.jsx` - Lista paginada de conversaciones con filtros
          - `Graficos.jsx` - Gráficos de evolución de alertas y síntomas
          - `RiesgoCard.jsx` - Tarjeta para mostrar puntuación de riesgo actual
          - `MetricasMadre.jsx` - Indicadores específicos de salud materna
          - `MetricasBebe.jsx` - Indicadores específicos del bebé
        - **`Layout/`**
          - `Header.jsx`
          - `Footer.jsx`
          - `AuthGuard.jsx` - Protege rutas que requieren autenticación
      - **`pages/`**
        - `LoginPage.jsx` - Página de ingreso con código de dispositivo
        - `OnboardingPage.jsx` - Primera vez: explicación y consentimiento
        - `ChatPage.jsx` - Página principal con el chat unificado
        - `ProgresoPage.jsx` - Página de dashboard con gráficos e historial
      - **`services/`**
        - `api.js` - Cliente HTTP para llamar al backend
        - `auth.js` - Manejo de tokens y sesión
      - **`styles/`**
        - `index.css`
      - **`utils/`**
        - `formatters.js` - Formato de fechas, textos, etc.
    - `.env.example`
    - `package.json`
    - `README.md`

  - `README.md` - Documentación principal del proyecto

---

## 👥 Roles y Responsabilidades por Persona

### 🧸 Jacobo Rincón – Hardware (Raspberry Pi + Componentes)

**Objetivo:** Construir el dispositivo físico funcional que pueda grabar audio, enviarlo al backend, recibir una respuesta de audio y reproducirla, con retroalimentación visual mediante LED.

**Responsabilidades principales:**

- Montar y cablear los componentes electrónicos:
  - **INMP441** (micrófono I2S) para capturar la voz.
  - **PCM5102A** (DAC I2S) + **LM386** (amplificador) + altavoz para reproducir respuestas.
  - Botón táctil para iniciar/detener la grabación.
  - **LED RGB** (o tres LEDs individuales) para indicar estado: grabando, procesando, error, listo.
- Configurar la **Raspberry Pi 4 Model B** con Raspberry Pi OS Lite y las librerías necesarias. Documentar el proceso de habilitación de I2S, ajustes de audio y configuración de red.
- Programar el firmware en Python que:
  - Espera la pulsación del botón.
  - Mientras el botón está presionado, graba audio en formato WAV con una duración máxima de 60 segundos (corte automático).
  - Cambia el color del LED según el estado (grabando, enviando, esperando respuesta, reproduciendo, error).
  - Envía el archivo de audio al backend mediante HTTP POST, incluyendo el identificador único del dispositivo en los headers.
  - Recibe la respuesta JSON que contiene la URL del audio generado y un texto de respaldo.
  - Descarga el audio y lo reproduce a través del altavoz mientras mantiene el LED indicador.
  - Maneja reconexión WiFi y reintentos de envío con backoff exponencial.
- Diseñar (con ayuda de impresión 3D) y ensamblar la carcasa con forma de animal, integrando todos los componentes de forma segura y estética, dejando accesible el botón y el LED.

**Entregables clave:**

- Código fuente en `hardware-firmware/src/` completo y comentado.
- Documentación de conexiones, calibración y configuración en `hardware-firmware/docs/`.
- Esquemas de cableado (fotos o diagramas).
- Demostración de funcionamiento: el dispositivo graba, envía y reproduce correctamente.

---

### 🧠 Juan Zamudio – Backend Principal + Transcripción + Extracción con LLM

**Objetivo:** Desarrollar el servidor FastAPI que sirva como orquestador central, exponiendo endpoints para el hardware y el frontend, integrando todos los servicios de procesamiento.

**Responsabilidades principales:**

- Configurar el proyecto FastAPI con estructura modular (endpoints, servicios, modelos).
- Implementar el endpoint `/api/v1/voz` que recibe el audio desde el hardware:
  - Validar API key del dispositivo.
  - Guardar temporalmente el archivo WAV.
  - Llamar al servicio de transcripción (Whisper) para obtener texto.
  - Invocar al servicio de extracción de datos (LLM) para obtener JSON estructurado (síntomas madre, síntomas bebé, duración, intensidad, etc.).
  - Integrar los servicios de Javier (motor de reglas, regresión logística, respuesta empática, TTS) en el flujo.
  - Guardar la interacción en la base de datos mediante los servicios de Gabriela.
  - Devolver al hardware la URL del audio generado y un texto de respaldo.
- Implementar el endpoint `/api/v1/chat` para el frontend:
  - Recibe texto del usuario.
  - Realiza el mismo flujo que el endpoint de voz, pero sin transcripción (el texto ya está disponible).
  - Guarda la interacción con origen “texto”.
- Implementar el endpoint `/api/v1/auth/register` para que el frontend pueda vincular un dispositivo mediante un código único (generado por el hardware).
- Implementar el endpoint `/api/v1/auth/token` para obtener JWT usando el código.
- Configurar **CORS** para permitir peticiones desde el frontend.
- Documentar automáticamente la API con Swagger (FastAPI lo hace por defecto).
- Implementar un sistema de colas para procesamiento asíncrono (usando Celery o FastAPI BackgroundTasks) para evitar timeouts en el hardware.
- Configurar logging centralizado y manejo de errores con respuestas adecuadas.
- Asegurar que el backend esté desplegado en un VPS o servicio en la nube (Railway, Render, etc.) con variables de entorno bien definidas.

**Entregables clave:**

- Código completo en `backend-api/app/`.
- Endpoints funcionando y documentados en `/docs`.
- Integración con Whisper, Groq y los servicios de Javier.
- Scripts de despliegue y configuración de entorno.
- Pruebas unitarias e integración en `backend-api/tests/`.

---

### 🩺 Javier Pérez – Motor de Reglas + Respuesta Empática + TTS + Regresión Logística

**Objetivo:** Proveer la lógica clínica, el modelo de riesgo, la generación de respuestas empáticas y la conversión a voz, asegurando que las recomendaciones sean precisas y el tono adecuado.

**Responsabilidades principales:**

- **Motor determinista de reglas clínicas** (`motor_reglas.py`):
  - Implementar reglas en Python puro (if-else) para clasificar en verde, amarillo o rojo, basado en síntomas de la madre y del bebé.
  - Priorizar reglas: emergencias > fiebre en bebé pequeño > deshidratación > mastitis > etc.
  - Devolver nivel de alerta, recomendación médica con fuente, lista de reglas activadas y un booleano `requiere_accion_inmediata`.
  - Incluir reglas detalladas documentadas en `docs/reglas_clinicas.md` con referencias médicas.

- **Modelo de regresión logística** (`regresion_logistica.py`):
  - Definir las 17 variables de entrada (las ya acordadas) y la variable objetivo (riesgo bajo/medio/alto).
  - Generar datos sintéticos realistas con `generar_datos_sinteticos.py` (al menos 2000 registros, balanceados).
  - Entrenar el modelo con `entrenar_modelo.py` y guardar el pipeline (escalador + modelo) en `models/ml/`.
  - Validar el modelo con validación cruzada y métricas (accuracy, precisión, recall). Documentar en `docs/modelo_riesgo.md`.
  - Proveer una función `predecir_riesgo(features)` que retorne una probabilidad y la clase.

- **Generación de respuesta empática** (`respuesta_empatica.py`):
  - Utilizar **Groq API** con modelo `llama3-70b-8192` o `mixtral-8x7b-32768`.
  - Construir un prompt que incluya: el texto original del usuario, los síntomas detectados, el nivel de alerta, la recomendación médica del motor de reglas y la puntuación de riesgo.
  - Solicitar una respuesta cálida, en español, que valide las emociones, explique brevemente la situación y ofrezca los pasos a seguir.
  - Asegurar que la respuesta no exceda los 300 caracteres para facilitar la TTS y la lectura.

- **Text‑to‑Speech** (`tts.py`):
  - Implementar con Google Cloud Text-to-Speech (voz femenina en español) como primera opción.
  - Incluir Coqui TTS como fallback local si no hay conexión a internet o la API falla.
  - Guardar los archivos MP3 en `static/audio/` con nombre único (UUID + timestamp).
  - Retornar la URL pública del archivo.

- **Limpieza de archivos** (`cleanup.py`):
  - Programar una tarea diaria (o ejecutarla al inicio) que elimine archivos MP3 con más de 7 días de antigüedad y mantenga un máximo de 1000 archivos.

- **Pruebas unitarias** en `tests/` para cada servicio.

**Entregables clave:**

- Todos los servicios implementados y documentados.
- Modelo de regresión logística entrenado y listo para producción.
- Documentación de reglas clínicas y modelo de riesgo.
- Integración con el backend principal a través de funciones claras.

---

### 🗄️ Gabriela Virgüez – Base de Datos + Endpoints de Historial y Progreso

**Objetivo:** Diseñar e implementar el esquema de base de datos, los scripts de migración, las funciones de acceso a datos y los endpoints REST que permitan al frontend consultar el historial y las estadísticas.

**Responsabilidades principales:**

- **Diseño de esquema PostgreSQL**:
  - Tabla `usuarios`:
    - `uuid` (UUID, PK)
    - `dispositivo_id` (VARCHAR(50), UNIQUE)
    - `codigo_registro` (VARCHAR(6), temporal, para vincular web)
    - `fecha_registro` (TIMESTAMP)
    - `fecha_consentimiento` (TIMESTAMP)
    - `anonimizado` (BOOLEAN, DEFAULT FALSE)
    - `fecha_anonimizacion` (TIMESTAMP)
  - Tabla `interacciones`:
    - `id` (SERIAL, PK)
    - `usuario_uuid` (UUID, FK a usuarios.uuid)
    - `fecha` (TIMESTAMP, DEFAULT NOW())
    - `origen` (VARCHAR(10): 'voz' o 'texto')
    - `texto_usuario` (TEXT)
    - `texto_respuesta` (TEXT)
    - `variables_extraidas` (JSONB): contiene síntomas madre, síntomas bebé, duración, intensidad, etc.
    - `sintomas_madre` (TEXT[]): array de strings con los síntomas detectados en la madre
    - `sintomas_bebe` (TEXT[]): array de strings con los síntomas detectados en el bebé
    - `nivel_alerta` (VARCHAR(10): 'verde', 'amarillo', 'rojo')
    - `puntuacion_riesgo` (FLOAT, entre 0 y 1)
    - `recomendaciones` (TEXT)
    - `fuente` (TEXT)
    - `reglas_activadas` (TEXT[])
    - `requiere_accion_inmediata` (BOOLEAN)
    - `feedback_util` (BOOLEAN, NULLABLE): para que la madre pueda indicar si la respuesta fue útil
  - Índices:
    - `idx_interacciones_usuario_fecha` ON (usuario_uuid, fecha)
    - `idx_interacciones_nivel` ON (nivel_alerta)
    - `idx_interacciones_riesgo` ON (puntuacion_riesgo)
  - Vistas materializadas para consultas frecuentes de gráficos.

- **Scripts de migración** versionados en `database-migrations/migrations/`.

- **Datos sintéticos** para pruebas (al menos 3 usuarios con 20-50 interacciones cada uno, variando niveles de alerta y síntomas).

- **Funciones de acceso a datos** en `backend-api/app/services/database.py`:
  - `guardar_interaccion(...)` - inserta una interacción.
  - `obtener_historial(usuario_uuid, limit, offset, filtros)` - devuelve lista paginada.
  - `obtener_resumen_progreso(usuario_uuid, periodo)` - devuelve estadísticas agregadas (número de interacciones por nivel, riesgo promedio, etc.).
  - `obtener_datos_graficos(usuario_uuid, agrupacion)` - devuelve series temporales para gráficos (fecha, conteo por nivel, etc.).
  - `registrar_feedback(interaccion_id, util)` - actualiza el feedback.

- **Endpoints REST** en `backend-api/app/api/v1/endpoints/historial.py`:
  - `GET /api/v1/historial` - lista de conversaciones con paginación y filtros (por fecha, nivel_alerta, origen).
  - `GET /api/v1/progreso/resumen` - estadísticas para el dashboard.
  - `GET /api/v1/progreso/grafico` - datos para gráficos de evolución.

- **Documentación** en `database-migrations/docs/SCHEMA.md` con el modelo de datos y ejemplos de consultas.

**Entregables clave:**

- Base de datos PostgreSQL funcionando en desarrollo y producción.
- Scripts de migración aplicados.
- Funciones de acceso a datos implementadas y probadas.
- Endpoints de historial y progreso listos para ser consumidos por el frontend.

---

### 🎨 Manuela Vergara – Frontend Web (React + Tailwind)

**Objetivo:** Construir la aplicación web que permita a la madre interactuar por chat de texto con la misma inteligencia artificial del dispositivo, consultar el historial unificado (voz y texto) y visualizar su progreso a través de gráficos.

**Responsabilidades principales:**

- Configurar el proyecto con **Vite + React** y **Tailwind CSS**.
- Implementar **autenticación**:
  - Página de login donde se ingresa un código de 6 dígitos (generado por el dispositivo).
  - Almacenar JWT en localStorage y adjuntarlo en cada petición.
  - Ruta protegida que redirige al login si no hay token.
- Crear página de **onboarding** para la primera vez: mostrar información del proyecto, solicitar consentimiento informado y guardar la aceptación en el backend.
- **Chat unificado**:
  - Un área de chat que muestre tanto los mensajes de voz (enviados desde el dispositivo) como los mensajes de texto escritos en la web.
  - Cada mensaje debe indicar el origen (voz o texto), la fecha/hora, el contenido, y la respuesta del sistema.
  - El usuario puede escribir un mensaje de texto y enviarlo; se debe mostrar el estado de "escribiendo..." y la respuesta del sistema en tiempo real.
  - El historial del chat se obtiene del endpoint de historial, mostrando los últimos mensajes con paginación infinita.
- **Dashboard de progreso**:
  - Tarjeta con la puntuación de riesgo actual (última interacción) y su evolución.
  - Gráficos de barras/líneas que muestren la evolución de las alertas (verde, amarillo, rojo) a lo largo del tiempo (días, semanas).
  - Gráficos separados para los síntomas más frecuentes de la madre y del bebé (usando los arrays de síntomas de la BD).
  - Selector de período (última semana, último mes, personalizado).
- **Historial completo**:
  - Lista paginada de todas las interacciones con filtros por nivel de alerta, origen (voz/texto) y fecha.
  - Cada elemento puede expandirse para mostrar los detalles completos: síntomas detectados, recomendación, puntuación de riesgo, etc.
  - Botón para exportar el historial a PDF o CSV.
- **Feedback del usuario**:
  - Después de cada respuesta del sistema, mostrar un pequeño componente con dos botones (útil / no útil) para registrar feedback.
  - Enviar esa información al backend mediante el endpoint correspondiente.
- **Manejo de estados**:
  - Mostrar skeletons o spinners mientras se cargan los datos.
  - Manejar errores de red con mensajes amigables y opciones de reintento.
- **Responsive y accesibilidad**:
  - Diseño funcional en móviles, tablets y escritorio.
  - Navegación por teclado, etiquetas ARIA básicas.

**Entregables clave:**

- Código fuente completo en `frontend-web/src/`.
- Aplicación desplegada en un servicio de hosting (Vercel, Netlify, etc.) y conectada al backend.
- Documentación de cómo correr el proyecto localmente.

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
| **LED RGB** | Proporciona retroalimentación visual: rojo = grabando, amarillo parpadeando = procesando, verde = listo, rojo fijo = error. |
| **Batería / Fuente de alimentación** | Para que el dispositivo sea portátil (se recomienda una batería portátil USB‑C que pueda alimentar la Raspberry Pi). |

---

## 🔄 Flujo General de Datos

1. **La mamá presiona el botón** del animal y habla sobre su estado o el del bebé.
2. **La Raspberry Pi** graba el audio (máx 60s) mientras el botón está presionado, lo guarda temporalmente como WAV y lo envía mediante HTTP POST al endpoint `/api/v1/voz` del backend, incluyendo el `X-Device-Id` en los headers.
3. **El backend (FastAPI)** recibe el audio, verifica el dispositivo, lo encola en un sistema de tareas en segundo plano para no bloquear al hardware.
4. La tarea en segundo plano:
   - Transcribe el audio con Whisper a texto.
   - Extrae datos estructurados con Groq LLM (síntomas madre, síntomas bebé, duración, intensidad, etc.).
   - Aplica el motor de reglas y obtiene nivel de alerta y recomendación médica.
   - Calcula la puntuación de riesgo con el modelo de regresión logística.
   - Genera la respuesta empática con Groq LLM.
   - Convierte la respuesta a audio MP3 con TTS y guarda el archivo.
   - Almacena toda la interacción en la base de datos.
   - Actualiza el estado de la tarea con la URL del audio.
5. El hardware, mientras tanto, mantiene una espera activa (polling) o recibe una notificación vía WebSocket (opcional) y descarga el audio para reproducirlo.
6. La mamá también puede acceder al **frontend web** desde su teléfono o computadora, donde:
   - Se autentica usando el código del dispositivo.
   - Accede a un chat unificado donde ve todas las interacciones pasadas (tanto las de voz como las que ella escribe por texto).
   - Puede escribir un nuevo mensaje, que sigue el mismo flujo de procesamiento (excepto transcripción) y la respuesta se muestra en el chat.
   - Consulta gráficos de evolución de su salud y la del bebé.

---

## 📊 Especificación Detallada de la Base de Datos

### Tabla `usuarios`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| uuid | UUID | Identificador único del usuario (PK) |
| dispositivo_id | VARCHAR(50) | ID único del dispositivo físico (se graba en firmware) |
| codigo_registro | VARCHAR(6) | Código temporal de 6 dígitos para vincular la web al dispositivo (válido 24h) |
| fecha_registro | TIMESTAMP | Fecha de creación del usuario |
| fecha_consentimiento | TIMESTAMP | Fecha en que la madre aceptó el consentimiento informado |
| anonimizado | BOOLEAN | Indica si los datos ya fueron anonimizados |
| fecha_anonimizacion | TIMESTAMP | Fecha de anonimización |

### Tabla `interacciones`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | SERIAL | Identificador numérico de la interacción |
| usuario_uuid | UUID | FK a usuarios.uuid |
| fecha | TIMESTAMP | Fecha y hora de la interacción |
| origen | VARCHAR(10) | 'voz' o 'texto' |
| texto_usuario | TEXT | Texto original del usuario (transcrito o escrito) |
| texto_respuesta | TEXT | Respuesta generada por el sistema |
| variables_extraidas | JSONB | Estructura flexible con todos los campos extraídos por el LLM (síntomas madre, síntomas bebé, duración, intensidad, etc.) |
| sintomas_madre | TEXT[] | Array de strings con los síntomas identificados en la madre |
| sintomas_bebe | TEXT[] | Array de strings con los síntomas identificados en el bebé |
| nivel_alerta | VARCHAR(10) | 'verde', 'amarillo', 'rojo' |
| puntuacion_riesgo | FLOAT | Valor continuo entre 0 y 1 de riesgo |
| recomendaciones | TEXT | Recomendación médica generada por el motor de reglas |
| fuente | TEXT | Fuente de la recomendación (ej. "Guía AEPED") |
| reglas_activadas | TEXT[] | Lista de reglas que se dispararon |
| requiere_accion_inmediata | BOOLEAN | Indica si se debe contactar a emergencias |
| feedback_util | BOOLEAN | NULL si no se ha dado feedback; true/false según respuesta del usuario |

### Índices recomendados

- `idx_interacciones_usuario_fecha` en (usuario_uuid, fecha) para ordenar historial.
- `idx_interacciones_nivel` en (nivel_alerta) para filtrar rápidamente.
- `idx_interacciones_riesgo` en (puntuacion_riesgo) para análisis.

### Política de anonimización

- Cada noche, un script revisa usuarios que llevan más de un año sin actividad.
- Sustituye `texto_usuario` y `texto_respuesta` por "ANONIMIZADO".
- Limpia `variables_extraidas` dejando solo los arrays de síntomas (sin valores numéricos).
- Marca `anonimizado = true` y registra fecha.

---

## 🔐 Autenticación y Seguridad

- **Hardware → Backend**: Cada dispositivo tiene un `dispositivo_id` único quemado en el firmware. El backend valida este ID mediante una API key generada en el momento del registro y almacenada en la tabla `usuarios`.
- **Frontend → Backend**:
  - Al iniciar, el hardware muestra en su pantalla (o por voz) un código de 6 dígitos (válido 24h) que la madre debe ingresar en la web.
  - La web envía el código al endpoint `/api/v1/auth/register` y recibe un JWT con validez de 30 días.
  - Todas las peticiones autenticadas incluyen el JWT en el header `Authorization: Bearer <token>`.
- **Comunicación**: Todo el tráfico debe ir por HTTPS (usar Let's Encrypt).

---

## 🤖 Selección de Tecnologías de IA

- **LLM para extracción y respuesta empática**: **Groq API** con modelos `llama3-70b-8192` (extracción) y `mixtral-8x7b-32768` (respuesta). Se elige por su baja latencia, calidad en español y facilidad de integración. Se utilizará un fallback con Ollama local en caso de caída de internet.
- **Whisper**: Se usará `whisper-ctranslate2` para transcripción rápida en español.
- **TTS**: Google Cloud Text-to-Speech como primera opción (voz femenina es-ES-Standard-A). Alternativa local: Coqui TTS.

---

## 🧪 Pruebas y Validación

- **Pruebas unitarias**: Cada servicio debe tener pruebas en `backend-api/tests/`.
- **Pruebas de integración**: Endpoints completos con base de datos de prueba.
- **Validación clínica**: Las reglas deben ser revisadas por un profesional de salud (se puede consultar a una matrona o pediatra) antes del despliegue final.
- **Pruebas de usuario**: Se realizarán con al menos 3 madres reales para obtener feedback sobre usabilidad y tono de las respuestas.

---

## 📦 Despliegue y Entorno

Inicialmente se prueba unicamente de manera local. No se hace despliege hasta haber probado totalmente el producto.

- **Backend**: Desplegar en un VPS (DigitalOcean, AWS EC2) o en plataformas como Railway o Render. Usar Docker para facilitar el despliegue.
- **Base de datos**: PostgreSQL en el mismo servidor o en un servicio administrado (Supabase, Neon).
- **Frontend**: Hosting estático en Vercel o Netlify.
- **Variables de entorno**: Documentar en `.env.example` todas las variables necesarias (Groq API key, Google Cloud credentials, URL de BD, etc.).

---

## 🗓️ Plan de Entregas para MVP (6 semanas)

### Semana 1-2: Base
- Jacobo: Configurar Raspberry Pi, pruebas de audio, botón, LED. Documentar.
- Juan: FastAPI base, endpoint /health, integración con Whisper, estructura de servicios.
- Javier: Motor de reglas con 5 reglas clave, generación de datos sintéticos, modelo de regresión base.
- Gabriela: Esquema BD, migraciones iniciales, funciones de guardado y consulta básicas.
- Manuela: Estructura React, autenticación mock, página de login y onboarding.

### Semana 3-4: Integración
- Jacobo: Integración con backend real (envío de audio, recepción de URL, reproducción).
- Juan: Endpoints /voz y /chat con colas asíncronas, integración de servicios de Javier.
- Javier: Modelo de regresión completo, respuesta empática con Groq, TTS básico.
- Gabriela: Endpoints de historial y progreso, carga de datos sintéticos.
- Manuela: Consumo de endpoints reales, chat unificado, gráficos simples.

### Semana 5-6: Pulido
- Jacobo: Mejoras de robustez (reintentos, LED), carcasa impresa.
- Juan: Documentación de API, despliegue en producción, variables de entorno.
- Javier: Limpieza de audios, pruebas unitarias, documentación de reglas y modelo.
- Gabriela: Anonimización automática, índices adicionales, backup.
- Manuela: Exportación de historial, feedback del usuario, responsive final.

---

*Este proyecto busca demostrar cómo la tecnología puede humanizarse para ofrecer compañía real, empática y clínicamente responsable en una de las etapas más importantes de la vida de una madre y su bebé, brindando apoyo integral que considera la salud y bienestar de ambos.*
