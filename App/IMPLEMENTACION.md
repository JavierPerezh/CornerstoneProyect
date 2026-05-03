# Guía de implementación — Cornerst App Móvil

Sigue los pasos en orden. No saltes ninguno.

---

## REQUISITOS PREVIOS

- Node.js 18 o superior → https://nodejs.org
- Git
- El backend de Cornerst corriendo (local o en VPS)
- Un teléfono físico Android o iOS, o un emulador configurado

---

## PASO 1 — Crear el proyecto Expo

```bash
npx create-expo-app VoiceAI-App --template blank-typescript
cd VoiceAI-App
```

---

## PASO 2 — Instalar dependencias

```bash
npx expo install expo-av
npx expo install expo-secure-store
npx expo install expo-router
npx expo install react-native-safe-area-context react-native-screens
```

---

## PASO 3 — Reemplazar la estructura generada

Borra todo lo que hay dentro de la carpeta `app/` y luego copia los archivos
entregados respetando esta estructura exacta:

```
VoiceAI-App/
├── app/
│   ├── _layout.tsx
│   ├── (auth)/
│   │   └── login.tsx
│   └── (main)/
│       ├── _layout.tsx
│       ├── index.tsx
│       ├── historial.tsx
│       └── ajustes.tsx
├── constants/
│   └── config.ts
├── services/
│   ├── auth.ts
│   └── api.ts
├── hooks/
│   └── useVoiceSession.ts
└── app.json          ← reemplazar el existente
```

---

## PASO 4 — Configurar la URL del backend

Abre `constants/config.ts` y cambia la línea:

```ts
export const BASE_URL = "https://tu-vps.com"; // ← CAMBIAR ESTO
```

**Opciones:**
- Backend en VPS: `"https://tu-dominio.com"` o `"http://IP_DEL_VPS:8000"`
- Backend local en la misma PC: `"http://192.168.X.X:8000"`
  - Obtén tu IP local con `ipconfig` (Windows) o `ifconfig` (Mac/Linux)
  - El teléfono y la PC deben estar en la misma red WiFi

---

## PASO 5 — Registrar la app como dispositivo en la BD

El endpoint `/voz` requiere que el `dispositivo_id` exista en la tabla `usuarios`.

Conéctate a PostgreSQL y ejecuta:

```sql
-- Para la cuenta demo (codigo_registro = 123456):
UPDATE usuarios
SET dispositivo_id = 'app-movil-001'
WHERE codigo_registro = '123456';

-- Para una cuenta real, reemplaza '123456' por el código de la paciente
```

Guarda el valor que pusiste (`app-movil-001` o el que elegiste) —
lo necesitarás en el Paso 8.

---

## PASO 6 — Configurar app.json

Reemplaza el `app.json` generado por el entregado. Solo cambia estos campos
si los necesitas personalizar:

```json
"ios": {
  "bundleIdentifier": "com.tuempresa.cornerst"  ← cambiar si publicas en App Store
},
"android": {
  "package": "com.tuempresa.cornerst"  ← cambiar si publicas en Play Store
}
```

---

## PASO 7 — Correr la app en desarrollo

```bash
npx expo start
```

Esto abre el menú de Expo. Luego:

- **Teléfono físico**: instala la app "Expo Go" en tu teléfono y escanea el QR
- **Emulador Android**: presiona `a` en la terminal (requiere Android Studio)
- **Simulador iOS**: presiona `i` en la terminal (solo en Mac, requiere Xcode)

---

## PASO 8 — Primera vez en la app (configuración inicial)

1. En la pantalla de login, ingresa el `codigo_registro` de 6 dígitos
   (o usa el botón **"Usar código demo (123456)"**)
2. Ve a la pestaña **Ajustes**
3. En el campo "Device ID" ingresa el `dispositivo_id` que registraste en el Paso 5
   (ej: `app-movil-001` o `device-demo-001` para la cuenta demo)
4. Presiona **Guardar**, luego **Probar** para verificar que el servidor lo acepta
5. Vuelve a la pestaña **Voz** — la app está lista para usar

---

## PASO 9 — Verificar que todo funciona

Prueba este flujo completo:

1. Presiona y mantén el botón de micrófono 🎙
2. Habla por 2-5 segundos
3. Suelta el botón
4. Espera: verás "Subiendo audio..." → "Procesando con IA..."
5. Después de ~10-20 segundos escucharás la respuesta de voz
6. El texto de la respuesta aparece en pantalla

Si falla, revisa:
- Que `BASE_URL` apunta al servidor correcto
- Que el servidor Cornerst está corriendo (`uvicorn app.main:app`)
- Que el `dispositivo_id` fue registrado en la BD (Paso 5)
- Que el teléfono tiene permisos de micrófono (iOS: Configuración → Expo Go → Micrófono)

---

## PASO 10 (opcional) — Build para producción

Para distribuir la app sin Expo Go:

```bash
# Instalar EAS CLI
npm install -g eas-cli

# Iniciar sesión en Expo
eas login

# Configurar el proyecto
eas build:configure

# Build para Android (.apk o .aab)
eas build --platform android

# Build para iOS (.ipa) — requiere cuenta de Apple Developer ($99/año)
eas build --platform ios
```

El APK de Android puede instalarse directamente en cualquier teléfono
sin pasar por la Play Store.

---

## ERRORES COMUNES

| Error | Causa | Solución |
|---|---|---|
| `Network request failed` | `BASE_URL` incorrecta o servidor apagado | Verificar IP y que Cornerst esté corriendo |
| `401 Unauthorized` en /voz | `dispositivo_id` no registrado en BD | Ejecutar el UPDATE del Paso 5 |
| `Código de registro inválido` | El código no existe en la tabla `usuarios` | Verificar con `SELECT * FROM usuarios` en PostgreSQL |
| `Permiso de micrófono denegado` | El sistema operativo bloqueó el acceso | Ir a Configuración del teléfono y activar el permiso |
| App no se conecta en red local | Teléfono y PC en redes distintas | Conectar ambos a la misma WiFi |
| `Tiempo de espera agotado` | El servidor tardó más de 60 segundos | Verificar que Whisper y Groq responden — revisar logs de uvicorn |
