"""
gpio_manager.py - Control de GPIO (LEDs y Botón)

Maneja:
- Control de LED RGB (PWM para intensidad)
- Detección de presión de botón (con debounce)
- Configuración de pines GPIO
- Limpieza de recursos al apagar
"""

import RPi.GPIO as GPIO
import threading
import time
import logging
from typing import Callable, Tuple

logger = logging.getLogger(__name__)


class LEDController:
    """
    Controlador de LED RGB.
    
    Soporta:
    - Control de color (RGB)
    - PWM para ajuste de intensidad
    - Operaciones seguras con threading
    """
    
    def __init__(self, pin_red: int, pin_green: int, pin_blue: int,
                 common_anode: bool = True, pwm_frequency: int = 1000):
        """
        Inicializa el controlador de LED.
        
        Args:
            pin_red: GPIO BCM número para LED Rojo
            pin_green: GPIO BCM número para LED Verde
            pin_blue: GPIO BCM número para LED Azul
            common_anode: True si es ánodo común, False si es cátodo común
            pwm_frequency: Frecuencia PWM en Hz (por defecto 1000 Hz)
        """
        self.pin_red = pin_red
        self.pin_green = pin_green
        self.pin_blue = pin_blue
        self.common_anode = common_anode
        self.pwm_frequency = pwm_frequency
        
        # Configuración de pines
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Configurar pines como salida
        GPIO.setup(self.pin_red, GPIO.OUT)
        GPIO.setup(self.pin_green, GPIO.OUT)
        GPIO.setup(self.pin_blue, GPIO.OUT)
        
        # Crear objetos PWM
        self.pwm_red = GPIO.PWM(self.pin_red, self.pwm_frequency)
        self.pwm_green = GPIO.PWM(self.pin_green, self.pwm_frequency)
        self.pwm_blue = GPIO.PWM(self.pin_blue, self.pwm_frequency)
        
        # Iniciar PWM en 0% (apagado)
        self.pwm_red.start(0)
        self.pwm_green.start(0)
        self.pwm_blue.start(0)
        
        self._lock = threading.Lock()
        
        logger.info(f"LEDController iniciado: R={pin_red}, G={pin_green}, B={pin_blue}")
    
    def set_color(self, color: Tuple[float, float, float], brightness: float = 1.0):
        """
        Establece el color del LED.
        
        Args:
            color: Tupla (R, G, B) con valores 0.0-1.0
            brightness: Brillo 0.0-1.0 (multiplicador)
        """
        with self._lock:
            try:
                r, g, b = color
                
                # Ajustar para ánodo común (invertir si es necesario)
                if self.common_anode:
                    r = 1.0 - r
                    g = 1.0 - g
                    b = 1.0 - b
                
                # Aplicar brillo (0-100 para PWM)
                r_pwm = max(0, min(100, r * brightness * 100))
                g_pwm = max(0, min(100, g * brightness * 100))
                b_pwm = max(0, min(100, b * brightness * 100))
                
                # Aplicar PWM
                self.pwm_red.ChangeDutyCycle(r_pwm)
                self.pwm_green.ChangeDutyCycle(g_pwm)
                self.pwm_blue.ChangeDutyCycle(b_pwm)
                
            except Exception as e:
                logger.error(f"Error configurando color LED: {e}")
    
    def pulse(self, color: Tuple[float, float, float], 
              duration: float = 1.0, cycles: int = None):
        """
        Pulsa el LED (aumenta y disminuye brillo).
        
        Args:
            color: Tupla RGB
            duration: Duración de un ciclo completo en segundos
            cycles: Número de ciclos (None = infinito)
        """
        def pulse_thread():
            cycle_count = 0
            while cycles is None or cycle_count < cycles:
                # Fade in
                for i in range(0, 101, 5):
                    if cycles is not None and cycle_count >= cycles:
                        break
                    brightness = i / 100.0
                    self.set_color(color, brightness)
                    time.sleep(duration / 40)
                
                # Fade out
                for i in range(100, -1, -5):
                    if cycles is not None and cycle_count >= cycles:
                        break
                    brightness = i / 100.0
                    self.set_color(color, brightness)
                    time.sleep(duration / 40)
                
                cycle_count += 1
        
        thread = threading.Thread(target=pulse_thread, daemon=True)
        thread.start()
        return thread
    
    def blink(self, color: Tuple[float, float, float],
              frequency: float = 1.0, duration: float = None):
        """
        Parpadea el LED (on/off rápido).
        
        Args:
            color: Tupla RGB
            frequency: Frecuencia en Hz
            duration: Duración total en segundos (None = infinito)
        """
        def blink_thread():
            period = 1.0 / frequency
            half_period = period / 2
            start_time = time.time()
            
            while True:
                if duration and (time.time() - start_time) > duration:
                    break
                
                self.set_color(color)
                time.sleep(half_period)
                self.set_color((0, 0, 0))
                time.sleep(half_period)
        
        thread = threading.Thread(target=blink_thread, daemon=True)
        thread.start()
        return thread
    
    def off(self):
        """Apaga el LED"""
        self.set_color((0, 0, 0))
    
    def cleanup(self):
        """Limpia recursos GPIO"""
        try:
            self.pwm_red.stop()
            self.pwm_green.stop()
            self.pwm_blue.stop()
            GPIO.cleanup([self.pin_red, self.pin_green, self.pin_blue])
            logger.info("LEDController cleaned up")
        except Exception as e:
            logger.error(f"Error limpiando LEDController: {e}")


class ButtonController:
    """
    Controlador de botón con debounce por software.
    
    Características:
    - Detección de presión (LOW = presionado con pull-up)
    - Debounce configurable (por defecto 50ms)
    - Callbacks para eventos de presión/liberación
    """
    
    def __init__(self, pin: int, debounce_ms: int = 50):
        """
        Inicializa el controlador de botón.
        
        Args:
            pin: GPIO BCM número del botón
            debounce_ms: Tiempo de debounce en milisegundos
        """
        self.pin = pin
        self.debounce_ms = debounce_ms / 1000.0
        
        # Configuración GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Pull-up interno
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Estado
        self._pressed = False
        self._last_press_time = 0
        self._lock = threading.Lock()
        
        # Callbacks
        self._on_press = None
        self._on_release = None
        
        # Thread de monitoreo
        self._monitor_thread = None
        self._stop_monitoring = threading.Event()
        
        logger.info(f"ButtonController iniciado en GPIO {pin}")
    
    def on_press(self, callback: Callable):
        """
        Registra callback cuando botón es presionado.
        
        Args:
            callback: Función a ejecutar sin argumentos
        """
        self._on_press = callback
    
    def on_release(self, callback: Callable):
        """
        Registra callback cuando botón es liberado.
        
        Args:
            callback: Función a ejecutar sin argumentos
        """
        self._on_release = callback
    
    def start_monitoring(self):
        """Inicia monitoreo de presiones"""
        self._stop_monitoring.clear()
        
        def monitor():
            while not self._stop_monitoring.is_set():
                current_state = GPIO.input(self.pin)
                
                # PIN LOW = presionado (pull-up activo)
                if current_state == GPIO.LOW:
                    if not self._pressed:
                        # Transición: NOT PRESSED → PRESSED
                        time.sleep(self.debounce_ms)
                        
                        # Verificar nuevamente después del debounce
                        if GPIO.input(self.pin) == GPIO.LOW:
                            with self._lock:
                                self._pressed = True
                                self._last_press_time = time.time()
                            
                            logger.debug("Botón presionado")
                            
                            if self._on_press:
                                try:
                                    self._on_press()
                                except Exception as e:
                                    logger.error(f"Error en callback on_press: {e}")
                else:
                    # PIN HIGH = liberado
                    if self._pressed:
                        time.sleep(self.debounce_ms)
                        
                        if GPIO.input(self.pin) == GPIO.HIGH:
                            with self._lock:
                                self._pressed = False
                            
                            logger.debug("Botón liberado")
                            
                            if self._on_release:
                                try:
                                    self._on_release()
                                except Exception as e:
                                    logger.error(f"Error en callback on_release: {e}")
                
                time.sleep(0.01)  # Poll cada 10ms
        
        self._monitor_thread = threading.Thread(target=monitor, daemon=True)
        self._monitor_thread.start()
        logger.info("Monitoreo de botón iniciado")
    
    def stop_monitoring(self):
        """Detiene monitoreo de botón"""
        self._stop_monitoring.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
        logger.info("Monitoreo de botón detenido")
    
    def is_pressed(self) -> bool:
        """Retorna True si el botón está presionado"""
        with self._lock:
            return self._pressed
    
    def press_duration(self) -> float:
        """Retorna cuántos segundos ha estado presionado (0 si no está presionado)"""
        with self._lock:
            if self._pressed:
                return time.time() - self._last_press_time
            return 0.0
    
    def cleanup(self):
        """Limpia recursos"""
        try:
            self.stop_monitoring()
            GPIO.cleanup(self.pin)
            logger.info("ButtonController cleaned up")
        except Exception as e:
            logger.error(f"Error limpiando ButtonController: {e}")


class GPIOManager:
    """
    Gestor centralizado de GPIO.
    Coordina LED y botón.
    """
    
    def __init__(self, config: dict):
        """
        Inicializa el gestor GPIO.
        
        Args:
            config: Diccionario con configuración:
                - gpio_led_red: Pin del LED rojo
                - gpio_led_green: Pin del LED verde
                - gpio_led_blue: Pin del LED azul
                - gpio_button: Pin del botón
        """
        # Controladores
        self.led = LEDController(
            pin_red=config.get('gpio_led_red', 27),
            pin_green=config.get('gpio_led_green', 23),
            pin_blue=config.get('gpio_led_blue', 24)
        )
        
        self.button = ButtonController(
            pin=config.get('gpio_button', 17)
        )
        
        logger.info("GPIOManager initialized")
    
    def startup(self, on_button_press: Callable = None, 
               on_button_release: Callable = None):
        """
        Inicia sistemas de GPIO.
        
        Args:
            on_button_press: Callback cuando botón se presiona
            on_button_release: Callback cuando botón se libera
        """
        if on_button_press:
            self.button.on_press(on_button_press)
        
        if on_button_release:
            self.button.on_release(on_button_release)
        
        self.button.start_monitoring()
        logger.info("GPIO systems started")
    
    def shutdown(self):
        """Apaga todos los sistemas GPIO"""
        self.button.stop_monitoring()
        self.led.off()
        
        # Esperar a que se limpien
        time.sleep(0.1)
        
        self.button.cleanup()
        self.led.cleanup()
        
        logger.info("GPIOManager shutdown")


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    """Test de GPIO"""
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n=== Test de GPIO ===\n")
    
    # Test LED
    print("Inicializando LED RGB...")
    led = LEDController(pin_red=27, pin_green=23, pin_blue=24)
    
    print("Rojo...")
    led.set_color((1, 0, 0))
    time.sleep(1)
    
    print("Verde...")
    led.set_color((0, 1, 0))
    time.sleep(1)
    
    print("Azul...")
    led.set_color((0, 0, 1))
    time.sleep(1)
    
    print("Púrpura...")
    led.set_color((1, 0, 1))
    time.sleep(1)
    
    print("Pulsando verde...")
    pulse_thread = led.pulse((0, 1, 0), duration=0.5, cycles=5)
    pulse_thread.join()
    
    print("Parpadeando rojo...")
    blink_thread = led.blink((1, 0, 0), frequency=2.0, duration=2.0)
    blink_thread.join()
    
    # Test Botón
    print("\nInicializando botón (presiona 3 veces)...")
    button = ButtonController(pin=17)
    
    press_count = 0
    
    def on_button_press():
        global press_count
        press_count += 1
        print(f"  [PRESIÓN {press_count}]")
    
    def on_button_release():
        duration = button.press_duration()
        print(f"  [LIBERADO] - Presionado {duration:.2f}s")
    
    button.on_press(on_button_press)
    button.on_release(on_button_release)
    button.start_monitoring()
    
    print("Esperando presiones de botón por 10 segundos...")
    time.sleep(10)
    
    button.stop_monitoring()
    
    # Cleanup
    print("\nLimpiando...")
    led.cleanup()
    button.cleanup()
    
    print("=== Test completado ===\n")
