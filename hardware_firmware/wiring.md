# Esquema de Cableado - Raspberry Pi Audio Device

## 📌 Referencia GPIO Raspberry Pi 4 Model B

```
                  ┌──────────────────────────┐
                  │  RASPBERRY PI 4 MODEL B  │
                  │     (Vista Superior)     │
                  └──────────────────────────┘

     3V3    GND    GPIO2   GPIO3    GPIO4   GND    GPIO17  GPIO27  GPIO22
    ●───●───●───●───●───●───●───●───●───●───●───●───●───●───●───
    ●───●───●───●───●───●───●───●───●───●───●───●───●───●───●───
    ●───●───●───●───●───●───●───●───●───●───●───●───●───●───●───

    Pin 1   GPIO18/SCLK  GPIO23/GREEN  GND    GPIO24/BLUE  GND
    ●───●───●───●───●───●───●───●───●───●───●───●───●───●───●───
    ●───●───●───●───●───●───●───●───●───●───●───●───●───●───●───
    ●───●───●───●───●───●───●───●───●───●───●───●───●───●───●───

    GND    GPIO25  GPIO8   GND    GPIO7   GPIO1   GND    GPIO12
    ●───●───●───●───●───●───●───●───●───●───●───●───●───●───●───
    ●───●───●───●───●───●───●───●───●───●───●───●───●───●───●───
    ●───●───●───●───●───●───●───●───●───●───●───●───●───●───●───

    GPIO16  GPIO20/DIN  GPIO21/DOUT  GND    GPIO26  GND    GPIO19/LRCK
    ●───●───●───●───●───●───●───●───●───●───●───●───●───●───●───
    ●───●───●───●───●───●───●───●───●───●───●───●───●───●───●───
```

## 🎤 Conexión INMP441 (Micrófono I2S)

### Pinout INMP441:
- `SD` (Serial Data) → GPIO 21 (BCM 21)
- `WS` (Word Select / LRCK) → GPIO 19 (BCM 19)
- `SCK` (Serial Clock) → GPIO 18 (BCM 18)
- `VDD` → 3V3
- `GND` → GND
- `L/R` → GND (mono, canal izquierdo)

### Tabla de Conexión:
| Pin INMP441 | Pin Raspberry Pi | Cable |
|---|---|---|
| VDD | 3V3 (Pin 1) | Rojo |
| GND | GND (Pin 6) | Negro |
| SCK | GPIO 18 (Pin 12) | Amarillo |
| WS | GPIO 19 (Pin 35) | Verde |
| SD | GPIO 21 (Pin 40) | Azul |
| L/R | GND (Pin 6) | Negro |

### Esquema ASCII (INMP441):
```
┌─────────────────────┐
│     INMP441         │
│   (Vista frontal)   │
└─────────────────────┘

Pin 1 (VDD)    ●─────●─ Pin 2 (N/C)
Pin 3 (GND)    ●─────●─ Pin 4 (L/R)
Pin 5 (WS)     ●─────●─ Pin 6 (SCK)
Pin 7 (SD)     ●─────●─ Pin 8 (N/C)

Cableado sugerido:
VDD    ──(Rojo)──→  3V3
GND    ──(Negro)→  GND (x2)
WS     ──(Verde)──→  GPIO 19
SCK    ──(Amarillo)─ GPIO 18
SD     ──(Azul)───→  GPIO 21
L/R    ──(Negro)→  GND
```

---

## 🔊 Conexión PCM5102A (DAC I2S)

### Pinout PCM5102A:
- `BCLK` (Bit Clock / SCK) → GPIO 18 (BCM 18)
- `DIN` (Data In) → GPIO 20 (BCM 20)
- `LRCK` (Word Select) → GPIO 19 (BCM 19)
- `3V3` → 3V3
- `GND` → GND (x2)
- `XMT` → 3V3 (habilitar transmisión)

### Tabla de Conexión:
| Pin PCM5102A | Pin Raspberry Pi | Cable |
|---|---|---|
| VCC | 3V3 (Pin 1) | Rojo |
| GND | GND (Pin 6) | Negro |
| BCLK | GPIO 18 (Pin 12) | Amarillo |
| DIN | GPIO 20 (Pin 38) | Azul |
| LRCK | GPIO 19 (Pin 35) | Verde |
| XMT | 3V3 (Pin 1) | Rojo |

### Esquema ASCII (PCM5102A):
```
┌─────────────────────┐
│    PCM5102A         │
│   (Vista frontal)   │
└─────────────────────┘

Pin 1 (VCC)    ●─────●─ Pin 2 (GND)
Pin 3 (BCLK)   ●─────●─ Pin 4 (DIN)
Pin 5 (LRCK)   ●─────●─ Pin 6 (GND)
Pin 7 (XMT)    ●─────●─ Pin 8 (N/C)

Cableado sugerido:
VCC    ──(Rojo)───→  3V3
GND    ──(Negro)→  GND (x2)
BCLK   ──(Amarillo)─ GPIO 18
DIN    ──(Azul)───→  GPIO 20
LRCK   ──(Verde)──→  GPIO 19
XMT    ──(Rojo)───→  3V3
```

---

## 🔉 Circuito de Amplificación (PCM5102A + LM386 + Altavoz)

### Conexión PCM5102A → LM386:

```
PCM5102A (DAC)
    ↓
┌──────────────────────┐
│   Capacitor 10µF     │  (AC coupling)
│  C1: (+) salida DAC  │
│      (-) entrada LM  │
└──────────────────────┘
         ↓
      LM386
      ┌─────┐
      │ +   │ ← Entrada (+) de PCM5102A
    ─├─────┤
      │ -   │ ← GND
      │ V+  │ ← 5V (o 9V para más potencia)
      │ V-  │ ← GND
      │ OUT │ ← Salida a altavoz
      └─────┘
```

### Tabla de Conexión LM386:

| Pin LM386 | Conexión | Notas |
|---|---|---|
| 1 (N/C) | Abierto | Ganancia baja |
| 2 (-IN) | GND vía 10kΩ | Entrada inversora |
| 3 (+IN) | PCM5102A vía 10µF cap | Entrada no-inversora |
| 4 (V-) | GND | Negativo |
| 5 (OUT) | Capacitor 10µF → Altavoz | Salida |
| 6 (V+) | 5V (recomendado 9V) | Alimentación positiva |
| 7 (GND) | GND | Tierra |
| 8 (BYPASS) | Capacitor 10µF a GND | Filtro de ruido |

### Esquema de Amplificador Completo:

```
      PCM5102A (L Channel)
            ↓
         ┌──────────────┐
         │ 10µF Cap C1  │
         └──────────────┘
              ↓
         ┌─────────────────────────┐
         │       LM386 DIP-8       │
    5V ──┤ V+ (Pin 6)              │
         │                         │
    GND─┤ V- (Pin 4)              │
         │                         │
    10kΩ─┤ -IN (Pin 2) ← GND      │
         │                         │
         │ +IN (Pin 3) ← (PCM C1)  │
         │                         │
         │ OUT (Pin 5)             │
         └─────────────────────────┘
              ↓
         ┌──────────────┐
         │ 10µF Cap C2  │
         └──────────────┘
              ↓
         [Altavoz 8Ω]
```

**Nota importante**: 
- Si usas alimentación de 5V: ganancia ≈ 20V/V (26dB)
- Si usas 9V: ganancia ≈ 200V/V (46dB)
- Para evitar retroalimentación acústica, ubicar micrófono y altavoz lo más alejados posible

---

## 🔘 Conexión Botón

### Esquema (Pull-up interno en GPIO 17):

```
     3V3
      │
      ├──────[10kΩ Resistencia]────┐
      │                            │
      │                        ┌───┴────┐
      │                        │ Botón  │
      │                        └───┬────┘
      │                            │
   GPIO17 (BCM 17) ◄──────────────┘
      │
     GND
```

### Tabla de Conexión:

| Componente | Pin | GPIO |
|---|---|---|
| Botón (Pad 1) | 3V3 (Pin 1) vía 10kΩ | - |
| Botón (Pad 2) | GPIO 17 (Pin 11) | BCM 17 |
| GND | GND (Pin 6) | - |

**Configuración en Python**:
```python
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Pull-up activado

# Lectura
if GPIO.input(17) == GPIO.LOW:
    print("Botón presionado")
```

---

## 💡 Conexión LED RGB

### Opción 1: LED RGB (Cátodo Común)

```
          VCC (3V3)
           ↑
           │
      [Resistencia común]
      (opcional, 220Ω)
           │
      ┌────┴────┬────────┬────────┐
      │         │        │        │
    [470Ω]   [470Ω]  [470Ω]  [470Ω]
      │         │        │        │
    GPIO27    GPIO23   GPIO24   GND
    (Rojo)    (Verde)  (Azul)  (Com)
```

### Tabla de Conexión LED RGB:

| Pin LED RGB | Pin Raspberry Pi | Resistencia | Color |
|---|---|---|---|
| Común (K) | GND (Pin 6) | - | - |
| R (Red) | GPIO 27 (Pin 13) | 470Ω | Rojo |
| G (Green) | GPIO 23 (Pin 16) | 470Ω | Verde |
| B (Blue) | GPIO 24 (Pin 18) | 470Ω | Azul |

### Opción 2: Tres LEDs Individuales

```
    3V3 ──[470Ω]──● Rojo   ──→ GPIO 27
    3V3 ──[470Ω]──● Verde  ──→ GPIO 23
    3V3 ──[470Ω]──● Azul   ──→ GPIO 24
    
    Todas las cátodos (-) van a GND
```

**Configuración en Python**:
```python
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.OUT)  # Rojo
GPIO.setup(23, GPIO.OUT)  # Verde
GPIO.setup(24, GPIO.OUT)  # Azul

# Rojo sólido
GPIO.output(27, GPIO.HIGH)
GPIO.output(23, GPIO.LOW)
GPIO.output(24, GPIO.LOW)
```

---

## 🔌 Resumen de Conexiones Globales

### Tabla Master (Todos los pines usados):

| GPIO | BCM | Función | Componente | Cable |
|---|---|---|---|---|
| Pin 1 | - | 3V3 | Múltiples | Rojo |
| Pin 6 | - | GND | Múltiples | Negro |
| Pin 11 | 17 | Botón | Push button | Verde |
| Pin 12 | 18 | I2S SCLK | INMP441, PCM5102A | Amarillo |
| Pin 13 | 27 | LED Rojo | RGB LED | Rojo/Naranja |
| Pin 16 | 23 | LED Verde | RGB LED | Verde |
| Pin 18 | 24 | LED Azul | RGB LED | Azul |
| Pin 35 | 19 | I2S LRCK | INMP441, PCM5102A | Violeta |
| Pin 38 | 20 | I2S DIN | PCM5102A | Azul claro |
| Pin 40 | 21 | I2S SD | INMP441 | Cian |

---

## 🛠️ Verificación de Conexiones

### Checklist Visual:

- [ ] Todos los cables rojo (3V3) conectados a pines 3V3 o 1
- [ ] Todos los cables negro (GND) conectados a GND o pines 6, 9, 14, 20, 25, 30, 34, 39
- [ ] INMP441: 6 cables (VDD, GND, SCK, WS, SD, L/R)
- [ ] PCM5102A: 6 cables (VCC, GND, BCLK, DIN, LRCK, XMT)
- [ ] LM386: Alimentado a 5V o 9V separado (si aplica)
- [ ] Botón: 3 conexiones (3V3 → 10kΩ → GPIO17 → GND)
- [ ] LED RGB: 4 cables (R, G, B a GPIO; común a GND)
- [ ] Altavoz: Conectado a salida LM386 con capacitor de acoplamiento

### Test de Continuidad:

```bash
# En Raspberry Pi con multímetro:
1. Verificar continuidad 3V3 → VDD componentes
2. Verificar continuidad GND → GND en todos lados
3. Verificar cada GPIO a su destino
4. Verificar que no hay cortocircuitos entre 3V3 y GND
```

---

## ⚡ Alimentación

### Recomendaciones:

- **Raspberry Pi**: PSU oficial de 5V 3A mínimo
- **LM386**: 5V-18V (recomendado 9V para mayor potencia)
- **Micrófono INMP441**: 3V3 (máximo 3.6V)
- **DAC PCM5102A**: 3V3 (máximo 3.6V)
- **LEDs**: 3V3 a través de resistencias 470Ω

### Esquema de Alimentación:

```
AC Wall ─→ [5V PSU] ─→ Raspberry Pi (5V)
                          ├─→ 3V3 (regulador interno)
                          │   ├→ INMP441 (3V3)
                          │   ├→ PCM5102A (3V3)
                          │   └→ LED RGB (3V3)
                          │
                          └─→ [Opcional: 9V PSU para LM386]
                              └→ LM386 (9V para +20V/V)
```

---

## 📐 Layout de Protoboard (si se usa)

```
+─────────────────────────────────────+
│ PROTOBOARD 400 HOLES (65×25 mm)     │
├─────────────────────────────────────┤
│ 3V3─────●●●●●●────────●────        │ (Rail 3V3)
│ GND─────●●●●●●────────●────        │ (Rail GND)
│                                     │
│ GPIO18  [INMP441] [PCM5102A]        │ (SCLK, I2S)
│ GPIO19  (LRCK compartido)           │
│ GPIO20  (DIN para PCM5102A)         │
│ GPIO21  (SD para INMP441)           │
│                                     │
│ GPIO17  [Botón] ──[10kΩ]            │
│                                     │
│ GPIO27  [LED R] ──[470Ω]            │
│ GPIO23  [LED G] ──[470Ω]            │
│ GPIO24  [LED B] ──[470Ω]            │
│                                     │
│ [LM386] ────→ [Altavoz]             │
│                                     │
+─────────────────────────────────────+
```

---

## 🔍 Pruebas de Hardware

### Test 1: Verificar GPIOs funcionan

```bash
# SSH a Raspberry Pi
ssh pi@raspberrypi.local

# Instalar gpio utility
sudo apt install wiringpi

# Test GPIO 27 (rojo)
gpio mode 27 out
gpio write 27 1    # LED enciende
gpio write 27 0    # LED apaga
```

### Test 2: Verificar I2S detectado

```bash
# Verificar tarjetas de sonido
aplay -l
arecord -l

# Debería mostrar:
# card 0: sndrpiaudi [snd_rpi_aud], device 0: HiFi multicodec (hwplug:0,0) []
```

### Test 3: Grabación de prueba

```bash
# Grabar 5 segundos en mono, 16kHz, 16-bit
arecord -t wav -f S16_LE -r 16000 -c 1 -d 5 test_record.wav

# Reproducir
aplay test_record.wav
```

---

## 📝 Solución de Problemas Comunes

| Problema | Síntoma | Solución |
|---|---|---|
| LED no enciende | GPIO escrito pero LED oscuro | Verificar resistencia 470Ω, polaridad del LED |
| Botón no responde | GPIO 17 siempre HIGH | Verificar resistencia 10kΩ y conexión a GND |
| Sin audio de micrófono | `arecord` genera archivo vacío | Habilitar I2S en `raspi-config`, verificar pinout INMP441 |
| Sin audio en altavoz | Nada en `aplay` | Verificar PCM5102A detectado, cable DIN correcto |
| I2S no detecta dispositivos | `aplay -l` vacío | `dtoverlay=i2s-mmap` en `config.txt` |
| Ruido blanco fuerte | Audio con hiss/ruido | Añadir capacitores de bypass 100nF en 3V3/GND |
| Distorsión en audio | Audio cortado o saturado | Reducir ganancia del LM386 o volumen entrada |

---

**Última actualización**: Abril 2026
**Versión**: 1.0
