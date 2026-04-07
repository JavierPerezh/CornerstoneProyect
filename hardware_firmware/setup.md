# Setup.md - Configuración Inicial de Raspberry Pi

## 📋 Requisitos Previos

- Raspberry Pi 4 Model B (2GB+ RAM recomendado)
- microSD card 16GB+ (Class 10)
- Lector de tarjetas
- PC con acceso a internet
- Cable Ethernet (recomendado para primera instalación)
- Monitor HDMI + teclado USB (alternativa a SSH)

---

## 1️⃣ Instalación de Raspberry Pi OS

### 1.1 Descargar e instalar Raspberry Pi Imager

Descargar desde: https://www.raspberrypi.org/downloads/

```bash
# En macOS
brew install raspberry-pi-imager

# En Linux
sudo apt install rpi-imager

# En Windows
# Descargar .exe desde sitio oficial
```

### 1.2 Grabar imagen en microSD

1. Abre **Raspberry Pi Imager**
2. Selecciona:
   - **OS**: "Raspberry Pi OS (Other)" → **Raspberry Pi OS Lite (32-bit)** 
     - O 64-bit si quieres: `Raspberry Pi OS Lite (64-bit)`
   - **Storage**: Tu microSD card
3. Haz clic en ⚙️ (engranaje) para configuración avanzada:
   - [x] Set hostname: `animal-pi` (o tu preferencia)
   - [x] Enable SSH: Activado
   - [x] Use password authentication
   - [x] Set username and password: 
     - Usuario: `pi`
     - Contraseña: `raspberry` (cambiar después!)
   - [x] Configure wireless LAN:
     - SSID: Tu nombre de WiFi
     - Password: Tu contraseña WiFi
     - Wireless LAN country: Seleccionar tu país
   - [x] Set locale settings:
     - Timezone: `America/Bogota` (o tu zona)
     - Keyboard layout: `es` (si usas teclado español)

4. Haz clic en **WRITE** y espera a que termine

---

## 2️⃣ Arranque Inicial

### 2.1 Inserta microSD en Raspberry Pi

1. Apaga la Raspberry Pi
2. Inserta la microSD en la ranura (lado inferior)
3. Conecta power (PSU 5V 3A)
4. Espera 60 segundos para primer boot

### 2.2 Conexión SSH

```bash
# En tu PC
ssh pi@animal-pi.local

# Si no funciona, intenta con IP
ssh pi@192.168.1.xxx  # Reemplaza con IP real

# Contraseña: raspberry
```

---

## 3️⃣ Configuración del Sistema

### 3.1 Actualizar sistema operativo

```bash
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
```

### 3.2 Cambiar contraseña (importante por seguridad)

```bash
passwd
# Ingresa nueva contraseña
```

### 3.3 Configuración de raspi-config

```bash
sudo raspi-config
```

**Opciones a activar:**

1. **Interfacing Options**
   - [ ] SSH → Enable
   - [ ] I2C → Enable
   - [ ] SPI → Disable (no necesario)
   - [ ] 1-Wire → Disable
   - [ ] Serial Port** → Disable (para evitar conflictos)

2. **Advanced Options**
   - [ ] Expand Filesystem (usar todo espacio microSD)
   - [ ] Memory Split:
     - GPU Memory: 16 MB (mínimo, no necesitamos gráficos)

3. **Localization**
   - [ ] Timezone: `America/Bogota`
   - [ ] Keyboard: `es` (Spanish)
   - [ ] WiFi Country: `CO` (Colombia)

4. **Performance Options** (opcional)
   - [ ] GPU Frequency: 500 MHz (máximo)
   - [ ] CPU Frequency: Dejar en auto

Selecciona **Finish** y reinicia:

```bash
sudo reboot
```

---

## 4️⃣ Habilitación de I2S

### 4.1 Editar config.txt

El I2S (Inter-IC Sound) es el protocolo que usaremos para audio digital. Necesita estar habilitado en el firmware.

```bash
sudo nano /boot/config.txt
```

Busca o añade estas líneas al final del archivo:

```ini
# ========== I2S Audio Configuration ==========

# Habilitar soporte I2S (ALSA)
dtparam=i2s=on

# Device tree overlay para HiFi Audio
# (si usas tarjeta de sonido específica)
# dtoverlay=i2s-mmap

# Deshabilitar sonido integrado Broadcom
dtoverlay=disable-bt
dtparam=audio=on

# ========== GPIO Configuration ==========

# Reasignar UART1 si es necesario (para liberar GPIOs)
# dtoverlay=uart1

# ========== Memoria GPU ==========
gpu_mem=16
```

Guarda con `Ctrl+X`, `Y`, `Enter`.

### 4.2 Reboot para aplicar cambios

```bash
sudo reboot
```

---

## 5️⃣ Instalación de Dependencias Base

### 5.1 Herramientas del sistema

```bash
sudo apt install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    git \
    wget \
    curl \
    vim \
    htop

# Verificar Python 3
python3 --version
# Debería mostrar: Python 3.9.x o superior
```

### 5.2 Librerías de audio (ALSA)

```bash
sudo apt install -y \
    alsa-utils \
    alsa-tools \
    libasound2-dev \
    libasound2-plugins

# Verificar que audio está disponible
aplay -l
arecord -l
# Debería mostrar:
# card X: sndrpiaudi [snd_rpi_aud], device 0: HiFi multicodec...
```

### 5.3 Herramientas de audio (opcional pero recomendado)

```bash
sudo apt install -y \
    sox \
    libsox-fmt-all \
    ffmpeg

# Verificar instalación
sox --version
ffmpeg -version
```

### 5.4 Librerías de desarrollo para audio en Python

```bash
sudo apt install -y \
    portaudio19-dev \
    libportaudio2

# Estas permiten compilar PyAudio
```

---

## 6️⃣ Instalación de Python Packages

### 6.1 Crear archivo requirements.txt

```bash
cd ~
nano requirements.txt
```

Copia este contenido:

```txt
# Audio and DSP
pyaudio==0.2.13
soundfile==0.12.1
numpy==1.24.3
scipy==1.11.1

# GPIO and Hardware
RPi.GPIO==0.7.0
gpiozero==2.0.1

# Networking
requests==2.31.0

# Utilities
python-dotenv==1.0.0

# Logging and monitoring
colorlog==6.7.0

# Optional: Testing
pytest==7.4.0
pytest-cov==4.1.0
```

Guarda con `Ctrl+X`, `Y`, `Enter`.

### 6.2 Instalar dependencias Python

```bash
# Actualizar pip
pip3 install --upgrade pip setuptools wheel

# Instalar packages
pip3 install -r requirements.txt

# Esto puede tomar 10-15 minutos en Raspberry Pi
# (compilación de módulos C en RPi es lenta)
```

**Nota**: Si PyAudio falla, intenta:

```bash
pip3 install --no-cache-dir pyaudio
# o instala desde fuente:
# pip3 install git+https://github.com/jgeboski/pyaudio-0.2.11.git
```

---

## 7️⃣ Pruebas de Audio Básicas

### 7.1 Test de grabación

```bash
# Grabar 5 segundos de audio mono
arecord -t wav -f S16_LE -r 16000 -c 1 -d 5 ~/test_record.wav

# Listar archivos creados
ls -lh ~/test_record.wav

# Reproducir
aplay ~/test_record.wav
```

**Esperado**: Deberías escuchar tu voz grabada.

### 7.2 Test de reproducción

```bash
# Si aún no hay archivo, crear uno de prueba con sox
sox -n -r 16000 -c 1 ~/test_tone.wav synth 3 sine 1000

# Reproducir
aplay ~/test_tone.wav
```

**Esperado**: Deberías escuchar un tono de 1000 Hz durante 3 segundos.

### 7.3 Verificar niveles de audio

```bash
# Ver información de ALSA
aplay -l
arecord -l

# Ajustar mezclador (si aplica)
alsamixer

# Salir con ESC
```

---

## 8️⃣ Configuración de GPIO y Permisos

### 8.1 Grupo GPIO

Para usar GPIO sin `sudo`, añade tu usuario al grupo `gpio`:

```bash
sudo usermod -a -G gpio pi

# Logout y login para que surta efecto
exit
# Reconectar SSH:
ssh pi@animal-pi.local
```

### 8.2 Verificar permisos

```bash
# Listar grupos del usuario
groups

# Debería incluir: pi adm gpio...
```

---

## 9️⃣ Configuración de Red

### 9.1 Verificar conectividad WiFi

```bash
# Ver conexión actual
iwconfig

# Ver IP asignada
hostname -I

# Ver velocidad conexión
wpa_cli status
```

### 9.2 Configurar WiFi estática (opcional)

Si necesitas IP fija, edita:

```bash
sudo nano /etc/dhcpcd.conf
```

Añade al final:

```ini
interface wlan0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=8.8.8.8 8.8.4.4
```

Reinicia networking:

```bash
sudo systemctl restart dhcpcd
```

---

## 🔟 Instalación del Código del Proyecto

### 10.1 Clonar repositorio

```bash
cd ~
git clone https://github.com/TU_USUARIO/hardware-firmware.git
cd hardware-firmware
```

O si aún no tienes repo, crear estructura:

```bash
mkdir -p ~/hardware-firmware/{src,docs,tests,cad,resources,systemd}
cd ~/hardware-firmware
```

### 10.2 Instalar dependencias del proyecto

```bash
cd ~/hardware-firmware/src
pip3 install -r requirements.txt
```

### 10.3 Crear archivo de configuración

```bash
nano ~/.env
```

Añade:

```bash
# Device Configuration
DEVICE_ID=animal-pi-001
DEVICE_NAME="Mi Animal de Audio"

# Backend Configuration
BACKEND_URL=http://localhost:8000
BACKEND_TIMEOUT=30

# Audio Configuration
SAMPLE_RATE=16000
AUDIO_CHUNK_SIZE=1024
MAX_RECORDING_SECONDS=60

# GPIO Configuration
GPIO_BUTTON=17
GPIO_LED_RED=27
GPIO_LED_GREEN=23
GPIO_LED_BLUE=24

# Logging
LOG_LEVEL=INFO
LOG_FILE=/home/pi/hardware-firmware/logs/device.log
```

---

## 1️⃣1️⃣ Autostart del Firmware (Systemd)

### 11.1 Crear archivo de servicio

```bash
sudo nano /etc/systemd/system/animal-device.service
```

Copia:

```ini
[Unit]
Description=Animal Device Audio Firmware
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/hardware-firmware
ExecStart=/usr/bin/python3 /home/pi/hardware-firmware/src/main.py
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=animal-device

# Limits
MemoryLimit=256M
CPUQuota=50%

[Install]
WantedBy=multi-user.target
```

### 11.2 Habilitar y probar servicio

```bash
# Recargar systemd
sudo systemctl daemon-reload

# Habilitar servicio en boot
sudo systemctl enable animal-device.service

# Iniciar servicio
sudo systemctl start animal-device.service

# Ver estado
sudo systemctl status animal-device.service

# Ver logs en tiempo real
sudo journalctl -u animal-device.service -f
```

---

## 1️⃣2️⃣ Checklist Final

Verifica que todo está funcionando:

- [ ] Raspberry Pi arranca y conecta a WiFi
- [ ] SSH accesible desde `pi@animal-pi.local`
- [ ] `python3 --version` muestra Python 3.9+
- [ ] `pip3 list` incluye numpy, scipy, requests, RPi.GPIO, pyaudio
- [ ] `aplay -l` muestra tarjeta de sonido HiFi
- [ ] `arecord -l` muestra entrada de audio
- [ ] Grabación de 5s con `arecord` genera archivo .wav
- [ ] Reproducción con `aplay` produce audio
- [ ] GPIO permisos sin `sudo` (usuario en grupo gpio)
- [ ] Archivo `~/.env` existe con configuración
- [ ] Servicio systemd crea sin errores
- [ ] `sudo systemctl start animal-device` arranca el firmware

---

## 🆘 Troubleshooting

### Problema: SSH no conecta

```bash
# En Raspberry Pi (con monitor)
hostname -I

# Luego desde PC
ssh pi@<IP_MOSTRADA>

# O usar discovery
arp-scan --localnet  # En Linux/Mac
```

### Problema: I2S no aparece en `aplay -l`

```bash
# Verificar overlay en config.txt
grep i2s /boot/config.txt

# Editar si falta:
sudo nano /boot/config.txt
# Añadir: dtparam=i2s=on

sudo reboot
```

### Problema: PyAudio no instala

```bash
# Intentar instalación alternativa
pip3 install --no-cache-dir pyaudio

# O compilar desde fuente (lento en Pi):
pip3 install --no-binary :all: pyaudio

# O usar sounddevice como alternativa:
pip3 install sounddevice
```

### Problema: Audio muy bajo/sin sonido

```bash
# Verificar volumen en alsamixer
alsamixer

# Usar flechas para ajustar
# ESC para salir

# O command line
amixer cset numid=3 100  # Volumen máximo
```

### Problema: Latencia alta de audio

```bash
# Reducir buffer size en Python
# Usar CHUNK_SIZE más pequeño (256 o 512 en lugar de 1024)

# Verificar que no hay otros procesos pesados
top
htop
```

---

## 📊 Información Útil Post-Setup

### Ver información del sistema

```bash
cat /proc/cpuinfo
cat /proc/meminfo
vcgencmd measure_temp
```

### Monitoreo de recursos

```bash
# Instalación de herramientas de monitoreo
sudo apt install bmon nethogs iotop

# Ver uso de CPU/RAM en tiempo real
top
# o
htop
```

### Backup de configuración

```bash
# Backup de archivos importantes
tar -czf ~/backup_config.tar.gz \
    ~/.env \
    /etc/dhcpcd.conf \
    /boot/config.txt \
    ~/hardware-firmware/

# Guardar en nube o PC externo
scp pi@animal-pi.local:~/backup_config.tar.gz ./
```

---

**Última actualización**: Abril 2026
**Versión**: 1.0
