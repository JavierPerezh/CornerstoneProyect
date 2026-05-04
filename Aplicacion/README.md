# Cornerst — App Móvil (React Native / Expo)

App móvil para el sistema de salud posparto **Cornerst**, basada en el esquema real de `init.sql` y los endpoints reales de `auth.py` y `voz.py`.

---

## Esquema de BD relevante (init.sql)

```sql
-- Un solo usuario tiene su dispositivo_id directamente en la fila
CREATE TABLE usuarios (
    uuid              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo_registro   VARCHAR(6) UNIQUE NOT NULL,  -- login de la paciente
    dispositivo_id    VARCHAR(120) UNIQUE,          -- X-Device-Id para /voz
    nombre            VARCHAR(120),
    email             VARCHAR(200)
    -- NO hay password — auth es por código de registro
);

-- Historial completo con síntomas, ML score y urgencia
CREATE TABLE interacciones (
    id                       BIGSERIAL PRIMARY KEY,
    usuario_uuid             UUID REFERENCES usuarios,
    texto_usuario            TEXT,
    texto_respuesta          TEXT,
    nivel_alerta             VARCHAR(20),       -- verde / amarillo / rojo
    puntuacion_riesgo        DOUBLE PRECISION,  -- score del modelo ML
    sintomas_madre           TEXT[],
    sintomas_bebe            TEXT[],
    requiere_accion_inmediata BOOLEAN,
    recomendaciones          TEXT,
    variables_extraidas      JSONB,
    reglas_activadas         JSONB
);
```

**Cuenta demo:** `codigo_registro = 123456`, `dispositivo_id = device-demo-001`

---

## Autenticación — dos mecanismos

| Endpoint      | Cómo                            | Campo BD              |
|---------------|---------------------------------|-----------------------|
| `/auth/login` | JSON `{ codigo_registro }`      | `usuarios.codigo_registro` |
| `/voz`        | Header `X-Device-Id`            | `usuarios.dispositivo_id`  |
| `/historial`  | JWT Bearer (del login)          | —                     |

---

## Flujo de voz (asíncrono con polling)

```
POST /voz  +  X-Device-Id  +  audio WAV
    → { task_id, status: "procesando" }   [HTTP 202, inmediato]

GET /voz/status/{task_id}  +  X-Device-Id   ← polling cada 2 seg
    → { status: "procesando" }
    → { status: "procesando" }
    → { status: "completado", audio_url, texto_respuesta }

Reproduce BASE_URL + audio_url  (MP3 Edge-TTS)
```

---

## Estructura final

```
VoiceAI-App/
├── constants/config.ts           ← BASE_URL, POLL_INTERVAL_MS, POLL_TIMEOUT_MS
├── services/
│   ├── auth.ts                   ← login(codigo_registro), device_id en SecureStore
│   └── api.ts                    ← procesarVoz(), obtenerHistorial()
├── hooks/useVoiceSession.ts      ← graba WAV → envía → polling → reproduce MP3
└── app/
    ├── _layout.tsx
    ├── (auth)/login.tsx          ← input de 6 dígitos, botón demo 123456
    └── (main)/
        ├── index.tsx             ← push-to-talk con estados: idle/recording/sending/processing/playing
        ├── historial.tsx         ← tabla interacciones con síntomas + score ML + urgencia
        ├── ajustes.tsx           ← configurar dispositivo_id + SQL de registro
        └── _layout.tsx           ← tabs: Voz | Historial | Ajustes
```

---

## Setup

```bash
npx create-expo-app VoiceAI-App --template blank-typescript
cd VoiceAI-App
npx expo install expo-av expo-secure-store expo-router
npx expo install react-native-safe-area-context react-native-screens
# Copiar todos los archivos entregados
```

**Único cambio obligatorio:**
```ts
// constants/config.ts
export const BASE_URL = "https://tu-vps.com";
```

Para desarrollo local: `http://192.168.x.x:8000`

---

## Registrar la app como dispositivo

```sql
UPDATE usuarios
SET dispositivo_id = 'app-movil-001'
WHERE codigo_registro = '123456';
```

Luego ingresar `app-movil-001` en la pantalla **Ajustes** de la app.

## Exportar repositorio a otro PC

```bash
git clone https://github.com/TU_USUARIO/cornerst-app.git
cd cornerst-app
# Para el backend
cd CornerstoneProyect
cp backend_api/.env.example backend_api/.env   # y editar con claves reales
docker compose up -d
# Para la app
cd ..
npm install
npx expo start
```
