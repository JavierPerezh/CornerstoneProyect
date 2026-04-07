# 🦁 Animal Device - Raspberry Pi Audio Firmware

Un dispositivo embebido en forma de animal que graba audio, lo envía a un backend para procesamiento, y reproduce la respuesta de audio con retroalimentación visual mediante LED RGB.

```
┌─────────────────────────────────────┐
│   GRABACIÓN → ENVÍO → RESPUESTA     │
│      LED Rojo   Orange   Verde      │
│                                     │
│  Micrófono I2S → Raspberry Pi 4 →   │
│      Altavoz DAC I2S                │
│                                     │
│  LED RGB RGB para estado actual     │
│  Botón tactil para control          │
└─────────────────────────────────────┘
```

---

## 🎯 Características

- ✅ **Grabación de audio** desde micrófono I2S (INMP441)
- ✅ **Reproducción de audio** en DAC I2S (PCM5102A) + amplificador LM386
- ✅ **Máquina de estados** con 6 estados diferentes
- ✅ **Retroalimentación visual** mediante LED RGB configurable
- ✅ **Control mediante botón** de presión táctil
- ✅ **Comunicación HTTP** con backend REST
- ✅ **Reconexión WiFi** automática con backoff exponencial
- ✅ **Manejo de errores** robusto
- ✅ **Logging** centralizado
- ✅ **Auto-start** mediante systemd

---

## 📋 Requisitos

### Hardware

- **Raspberry Pi 4 Model B** (2GB+ RAM recomendado)
- **microSD Card** 16GB+ (Class 10)
- **INMP441** - Micrófono I2S MEMS
- **PCM5102A** - DAC I2S
- **LM386** - Amplificador de audio
- **LED RGB** - Cátodo común
- **Botón táctil** - Pulsador NO
- **Altavoz** - 3-8Ω, 0.5-1W
- **Resistencias** - 470Ω (LEDs), 10kΩ (pull-up)
- **Capacitores** - 10µF, 100nF (desacoplamiento)
- **Cables y PSU** - 5V 3A mínimo

### Software

- **Raspberry Pi OS Lite** (32-bit o 64-bit)
- **Python 3.9+**
- **Dependencies**: Ver `src/requirements.txt`

---

## 🚀 Quick Start

### 1. Clonar Repositorio

```bash
cd ~
git clone https://github.com/JavierPerezh/CornerstoneProyect/tree/Hardware-(Jacobo)/hardware_firmware
cd hardware-firmware
```

### 2. Configurar Raspberry Pi

Seguir `docs/setup.md` para:
- Instalar Raspberry Pi OS
- Habilitar I2S
- Instalar dependencias Python
- Configurar variables de entorno

### 3. Conectar Hardware

Seguir `docs/wiring.md` para:
- Identificar pines GPIO
- Conectar INMP441 (micrófono)
- Conectar PCM5102A (DAC)
- Conectar LED RGB
- Conectar botón

### 4. Ejecutar Tests

```bash
# Test de hardware
python tests/test_hardware.py

# Deberías ver:
# ✓ GPIO (LED y Botón)
# ✓ Audio (Grabación y Reproducción)
# ✓ Red (Conectividad)
# ✓ Máquina de Estados
```

### 5. Iniciar Firmware

```bash
# Ejecución manual
cd src
python main.py

# O con systemd (auto-start)
sudo systemctl start animal-device.service
```

---

## 📁 Estructura del Proyecto

```
hardware-firmware/
├── PROJECT_PLAN.md              # Plan maestro del proyecto
│
├── docs/
│   ├── README.md                # Este archivo
│   ├── setup.md                 # Configuración Raspberry Pi
│   ├── wiring.md                # Esquema de cableado
│   ├── calibration.md           # Ajustes de audio
│   ├── api_spec.md              # Especificación del backend
│   └── troubleshooting.md       # Solución de problemas
│
├── src/
│   ├── main.py                  # Punto de entrada
│   ├── config.py                # Configuración centralizada
│   ├── state_machine.py         # Máquina de estados
│   ├── gpio_manager.py          # Control GPIO (LED/botón)
│   ├── audio_modules.py         # Grabación/reproducción
│   ├── network_manager.py       # HTTP y WiFi
│   ├── device_id_manager.py     # ID único del dispositivo
│   ├── logger_config.py         # Sistema de logging
│   ├── utils_and_config.py      # Utilidades
│   └── requirements.txt         # Dependencias Python
│
├── tests/
│   ├── test_hardware.py         # Test integral de hardware
│   ├── test_gpio.py             # Test unitario GPIO
│   ├── test_audio.py            # Test unitario Audio
│   ├── test_network.py          # Test unitario Red
│   └── backend_mock.py          # Backend mock para testing
│
├── cad/
│   ├── animal_design.step       # Modelo CAD
│   ├── animal_design.stl        # Para impresión 3D
│   └── parts/                   # Partes individuales
│
├── resources/
│   ├── demo_audio.wav           # Audio de prueba
│   └── default_response.wav     # Respuesta por defecto
│
└── systemd/
    └── animal-device.service    # Servicio systemd
```

---

## 🔌 Conexiones (Resumen)

| Componente | GPIO | Pin | Cable |
|---|---|---|---|
| INMP441 VDD | - | 3V3 | Rojo |
| INMP441 GND | - | GND | Negro |
| INMP441 SCK | BCM 18 | 12 | Amarillo |
| INMP441 WS | BCM 19 | 35 | Verde |
| INMP441 SD | BCM 21 | 40 | Azul |
| PCM5102A VCC | - | 3V3 | Rojo |
| PCM5102A DIN | BCM 20 | 38 | Azul |
| LED Rojo | BCM 27 | 13 | Naranja |
| LED Verde | BCM 23 | 16 | Verde |
| LED Azul | BCM 24 | 18 | Azul |
| Botón | BCM 17 | 11 | Gris |

**Ver `docs/wiring.md` para diagrama completo**

---

## 🎮 Uso

### Estado IDLE (LED Azul Pulsante)
Dispositivo listo esperando entrada del usuario.

### Presiona el Botón
Inicia grabación de audio (máximo 60 segundos).

### LED Rojo Sólido
Está grabando. Habla en el micrófono.

### Suelta el Botón
Detiene grabación y envía al backend.

### LED Naranja Pulsante
Enviando archivo al backend.

### LED Amarillo Sólido
Descargando respuesta.

### LED Verde Pulsante
Reproduciendo respuesta en el altavoz.

### LED Rojo Intermitente
Ha ocurrido un error. Espera 5 segundos para reintentar.

---

## ⚙️ Configuración

### Variables de Entorno (~/.env)

```bash
# Device
DEVICE_ID=animal-pi-001
DEVICE_NAME="Mi Animal de Audio"

# Audio
SAMPLE_RATE=16000
AUDIO_CHUNK_SIZE=1024
MAX_RECORDING_SECONDS=60

# GPIO
GPIO_BUTTON=17
GPIO_LED_RED=27
GPIO_LED_GREEN=23
GPIO_LED_BLUE=24

# Backend
BACKEND_URL=http://localhost:8000
BACKEND_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=/home/pi/hardware-firmware/logs/device.log
```

---

## 🔧 API del Backend

El firmware espera un backend REST que:

1. **POST /process_audio** - Recibe archivo WAV
   - Headers: `X-Device-ID: {uuid}`
   - Body: multipart/form-data con archivo audio
   - Response: JSON con `audio_url` y `text`

2. **GET /health** - Verificación de estado
   - Response: `{"status": "healthy"}`

3. **POST /device_info** - Envío de información del dispositivo
   - Body: JSON con info del sistema

Ver `docs/api_spec.md` para detalles completos y ejemplo de implementación.

---

## 📊 Máquina de Estados

```
        ┌──────────────────┐
        │   IDLE (AZUL)    │ ← Estado inicial
        └────────┬─────────┘
                 │ (botón presionado)
                 ↓
        ┌──────────────────┐
        │ RECORDING (ROJO) │
        └────────┬─────────┘
                 │ (botón soltado)
                 ↓
        ┌──────────────────┐
        │ SENDING (NARANJA)│
        └────────┬─────────┘
                 │ (respuesta recibida)
                 ↓
        ┌──────────────────┐
        │PROCESSING (AMARL)│
        └────────┬─────────┘
                 │ (audio descargado)
                 ↓
        ┌──────────────────┐
        │ PLAYING (VERDE)  │
        └────────┬─────────┘
                 │ (reproducción terminada)
                 ↓
        ┌──────────────────┐
        │   IDLE (AZUL)    │
        └──────────────────┘
        
Error en cualquier punto:
        ↓
        ┌──────────────────┐
        │ ERROR (ROJO LMP) │
        └────────┬─────────┘
                 │ (espera 5s)
                 ↓
        ┌──────────────────┐
        │   IDLE (AZUL)    │
        └──────────────────┘
```

---

## 🧪 Testing

### Test Integral del Hardware

```bash
cd hardware-firmware
python tests/test_hardware.py
```

Verifica:
- ✓ GPIOs (LED RGB y botón)
- ✓ Grabación y reproducción de audio
- ✓ Conectividad de red
- ✓ Máquina de estados

### Tests Unitarios

```bash
# Test específico
python tests/test_gpio.py
python tests/test_audio.py
python tests/test_network.py

# Con cobertura
pytest --cov=src tests/
```

### Backend Mock para Desarrollo

```bash
# En otra terminal
python tests/backend_mock.py

# Luego ejecutar firmware
python src/main.py
```

---

## 📝 Logs

### Ver logs en tiempo real

```bash
# Si está usando systemd:
sudo journalctl -u animal-device.service -f

# Si está ejecutando manualmente:
tail -f /home/pi/hardware-firmware/logs/device.log
```

### Rotación automática de logs

- Máximo 5 MB por archivo
- Se guardan hasta 5 backups
- Ubicación: `/home/pi/hardware-firmware/logs/`

---

## 🐛 Troubleshooting

Consulta `docs/troubleshooting.md` para:
- LED no enciende
- Botón no responde
- Sin audio de micrófono
- Sin audio en altavoz
- Ruido y distorsión
- Problemas de red y reconexión

Problemas comunes rápidos:

### Sin sonido de micrófono
```bash
# Verificar que I2S está habilitado
grep i2s /boot/config.txt

# Verificar dispositivo de audio
aplay -l
arecord -l
```

### LED no enciende
```bash
# Test de GPIO
python -c "
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.OUT)
GPIO.output(27, GPIO.HIGH)  # LED rojo debe encenderse
"
```

### Error de conexión HTTP
```bash
# Verificar conectividad
ping 8.8.8.8

# Verificar backend
curl http://localhost:8000/health
```

---

## 📦 Instalación de Dependencias

### Primera vez (en Raspberry Pi)

```bash
# Actualizar sistema
sudo apt update
sudo apt upgrade -y

# Instalar dependencias del sistema
sudo apt install -y python3-pip alsa-utils

# Instalar dependencias Python
cd ~/hardware-firmware/src
pip3 install -r requirements.txt
```

### Troubleshooting de PyAudio

```bash
# Si PyAudio falla
sudo apt install -y portaudio19-dev libportaudio2

# Instalar compilando
pip3 install --no-cache-dir pyaudio
```

---

## 🔐 Seguridad

- **Device ID**: UUID v4 único, almacenado localmente
- **Backend URL**: Configurar HTTPS en producción
- **Logs**: No incluyen datos sensibles
- **WiFi**: Usar contraseñas fuertes

---

## 📈 Optimizaciones de Performance

### Reducir latencia de audio
```bash
# En ~/.env
AUDIO_CHUNK_SIZE=512  # Default: 1024
SAMPLE_RATE=16000     # Min: 16000 Hz para voz
```

### Reducir consumo de memoria
```bash
# Monitorar
top
```

### Mejorar estabilidad de WiFi
```bash
# Habilitar roaming
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
# Añadir: bgscan="simple:30:-70:600"
```

---

## 🎨 Personalización de LEDs

En `src/state_machine.py`, modificar `_update_led()`:

```python
led_config = {
    DeviceState.IDLE: (LEDColor.BLUE, LEDState.PULSE),
    DeviceState.RECORDING: (LEDColor.RED, LEDState.SOLID),
    # ... etc
}
```

O usar directamente `gpio_manager.LEDController`:

```python
led.set_color((1, 0, 0))  # Rojo
led.pulse((0, 1, 0), duration=0.5)  # Verde pulsante
```

---

## 📞 Soporte y Recursos

- **Documentación oficial Raspberry Pi**: https://www.raspberrypi.org/documentation/
- **INMP441 Datasheet**: https://www.invensense.com/
- **PCM5102A Datasheet**: https://www.ti.com/
- **RPi.GPIO**: https://sourceforge.net/projects/raspberry-gpio-python/

---

## 📜 Licencia

Este proyecto es de código abierto. Libre para uso personal y educativo.

---

**Última actualización**: Abril 2026  
**Versión**: 1.0.0  
**Mantenedor**: Tu Nombre (@tu_usuario)
