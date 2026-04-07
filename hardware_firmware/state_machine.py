"""
state_machine.py - Máquina de Estados para Animal Device

Estados:
  - IDLE: Esperando presión de botón, LED azul pulsante
  - RECORDING: Grabando audio, LED rojo sólido
  - SENDING: Enviando archivo, LED naranja pulsante
  - PROCESSING: Descargando respuesta, LED amarillo
  - PLAYING: Reproduciendo audio, LED verde pulsante
  - ERROR: Error ocurrió, LED rojo intermitente
"""

from enum import Enum
from typing import Callable, Optional
from datetime import datetime
import threading
import time
import logging

logger = logging.getLogger(__name__)


class DeviceState(Enum):
    """Estados posibles del dispositivo"""
    IDLE = "idle"
    RECORDING = "recording"
    SENDING = "sending"
    PROCESSING = "processing"
    PLAYING = "playing"
    ERROR = "error"


class LEDState(Enum):
    """Estados visuales del LED"""
    OFF = "off"
    SOLID = "solid"
    PULSE = "pulse"
    BLINK = "blink"


class LEDColor:
    """Definición de colores RGB"""
    BLUE = (0, 0, 1)      # Azul (IDLE)
    RED = (1, 0, 0)       # Rojo (RECORDING)
    ORANGE = (1, 0.5, 0)  # Naranja (SENDING)
    YELLOW = (1, 1, 0)    # Amarillo (PROCESSING)
    GREEN = (0, 1, 0)     # Verde (PLAYING)
    WHITE = (1, 1, 1)     # Blanco (reserva)
    OFF = (0, 0, 0)       # Apagado


class StateMachine:
    """
    Máquina de estados para controlar el flujo del dispositivo.
    
    Maneja:
    - Transiciones de estado
    - Callbacks al entrar/salir de estados
    - Control del LED según estado
    - Timeouts y errores
    """
    
    def __init__(self, led_controller, button_controller):
        """
        Inicializa la máquina de estados.
        
        Args:
            led_controller: Objeto que controla los LEDs (gpio_manager.LEDController)
            button_controller: Objeto que detecta presión de botón
        """
        self.led_controller = led_controller
        self.button_controller = button_controller
        
        # Estado actual
        self._current_state = DeviceState.IDLE
        self._previous_state = None
        self._state_start_time = datetime.now()
        
        # Callbacks
        self._callbacks = {
            DeviceState.IDLE: {},
            DeviceState.RECORDING: {},
            DeviceState.SENDING: {},
            DeviceState.PROCESSING: {},
            DeviceState.PLAYING: {},
            DeviceState.ERROR: {},
        }
        
        # Thread para pulsación del LED
        self._pulse_thread = None
        self._pulse_stop_event = threading.Event()
        
        # Timeouts
        self.timeout_recording = 60  # segundos
        self.timeout_sending = 30
        self.timeout_processing = 30
        self.timeout_playing = 120
        
        logger.info("StateMachine initialized")
    
    @property
    def current_state(self) -> DeviceState:
        """Retorna el estado actual"""
        return self._current_state
    
    @property
    def state_duration(self) -> float:
        """Retorna segundos en estado actual"""
        return (datetime.now() - self._state_start_time).total_seconds()
    
    def register_callback(self, state: DeviceState, 
                         trigger: str, callback: Callable):
        """
        Registra un callback para un evento de estado.
        
        Args:
            state: Estado al que aplica el callback
            trigger: 'enter' o 'exit'
            callback: Función a ejecutar
        """
        if trigger not in ['enter', 'exit']:
            raise ValueError("trigger debe ser 'enter' o 'exit'")
        
        self._callbacks[state][trigger] = callback
        logger.debug(f"Callback registrado: {state.value} on_{trigger}")
    
    def transition_to(self, new_state: DeviceState, 
                     reason: str = ""):
        """
        Realiza transición a un nuevo estado.
        
        Args:
            new_state: Estado destino
            reason: Razón de la transición (para logs)
        """
        if new_state == self._current_state:
            logger.debug(f"Transición ignorada: ya en {new_state.value}")
            return
        
        old_state = self._current_state
        
        # Ejecutar callback exit del estado anterior
        if 'exit' in self._callbacks[old_state]:
            try:
                self._callbacks[old_state]['exit']()
            except Exception as e:
                logger.error(f"Error en callback exit de {old_state.value}: {e}")
        
        # Actualizar estado
        self._current_state = new_state
        self._previous_state = old_state
        self._state_start_time = datetime.now()
        
        # Actualizar LED
        self._update_led()
        
        logger.info(f"Transición: {old_state.value} → {new_state.value} " +
                   f"({reason})" if reason else "")
        
        # Ejecutar callback enter del nuevo estado
        if 'enter' in self._callbacks[new_state]:
            try:
                self._callbacks[new_state]['enter']()
            except Exception as e:
                logger.error(f"Error en callback enter de {new_state.value}: {e}")
    
    def _update_led(self):
        """Actualiza el LED según el estado actual"""
        led_config = {
            DeviceState.IDLE: (LEDColor.BLUE, LEDState.PULSE),
            DeviceState.RECORDING: (LEDColor.RED, LEDState.SOLID),
            DeviceState.SENDING: (LEDColor.ORANGE, LEDState.PULSE),
            DeviceState.PROCESSING: (LEDColor.YELLOW, LEDState.SOLID),
            DeviceState.PLAYING: (LEDColor.GREEN, LEDState.PULSE),
            DeviceState.ERROR: (LEDColor.RED, LEDState.BLINK),
        }
        
        color, led_state = led_config[self._current_state]
        
        # Detener pulsación anterior si existe
        self._stop_pulse()
        
        if led_state == LEDState.SOLID:
            self.led_controller.set_color(color)
        elif led_state == LEDState.PULSE:
            self._start_pulse(color, frequency=1.0)
        elif led_state == LEDState.BLINK:
            self._start_pulse(color, frequency=2.0)
    
    def _start_pulse(self, color: tuple, frequency: float = 1.0):
        """Inicia pulsación del LED"""
        self._pulse_stop_event.clear()
        
        def pulse_loop():
            period = 1.0 / frequency
            half_period = period / 2
            
            while not self._pulse_stop_event.is_set():
                self.led_controller.set_color(color)
                time.sleep(half_period)
                
                self.led_controller.set_color(LEDColor.OFF)
                time.sleep(half_period)
        
        self._pulse_thread = threading.Thread(target=pulse_loop, daemon=True)
        self._pulse_thread.start()
    
    def _stop_pulse(self):
        """Detiene la pulsación del LED"""
        if self._pulse_thread and self._pulse_thread.is_alive():
            self._pulse_stop_event.set()
            self._pulse_thread.join(timeout=1.0)
            self._pulse_thread = None
        
        self.led_controller.set_color(LEDColor.OFF)
    
    def check_timeout(self) -> bool:
        """
        Verifica si ha ocurrido un timeout en el estado actual.
        
        Returns:
            True si hay timeout, False si no
        """
        timeouts = {
            DeviceState.RECORDING: self.timeout_recording,
            DeviceState.SENDING: self.timeout_sending,
            DeviceState.PROCESSING: self.timeout_processing,
            DeviceState.PLAYING: self.timeout_playing,
            DeviceState.IDLE: None,
            DeviceState.ERROR: None,
        }
        
        timeout = timeouts[self._current_state]
        if timeout and self.state_duration > timeout:
            logger.warning(f"Timeout en estado {self._current_state.value} " +
                          f"({self.state_duration:.1f}s > {timeout}s)")
            return True
        
        return False
    
    def get_state_info(self) -> dict:
        """Retorna información del estado actual"""
        return {
            'current_state': self._current_state.value,
            'duration': self.state_duration,
            'start_time': self._state_start_time.isoformat(),
            'previous_state': self._previous_state.value if self._previous_state else None,
        }
    
    def shutdown(self):
        """Limpia recursos antes de apagar"""
        self._stop_pulse()
        self.led_controller.set_color(LEDColor.OFF)
        logger.info("StateMachine shutdown")


class StateMachineManager:
    """
    Controlador de alto nivel de la máquina de estados.
    Maneja las transiciones basadas en eventos del sistema.
    """
    
    def __init__(self, state_machine: StateMachine,
                 audio_capture, audio_playback, network_manager):
        """
        Inicializa el administrador.
        
        Args:
            state_machine: Instancia de StateMachine
            audio_capture: Módulo de grabación de audio
            audio_playback: Módulo de reproducción
            network_manager: Módulo de red y HTTP
        """
        self.state_machine = state_machine
        self.audio_capture = audio_capture
        self.audio_playback = audio_playback
        self.network_manager = network_manager
        
        self._recording_file = None
        self._response_audio_file = None
        
        logger.info("StateMachineManager initialized")
    
    def on_button_pressed(self):
        """Botón fue presionado - inicia grabación"""
        if self.state_machine.current_state == DeviceState.IDLE:
            self.start_recording()
        elif self.state_machine.current_state == DeviceState.RECORDING:
            self.stop_recording()
    
    def start_recording(self):
        """Inicia grabación de audio"""
        logger.info("Iniciando grabación...")
        
        try:
            self.state_machine.transition_to(
                DeviceState.RECORDING,
                reason="Botón presionado"
            )
            
            # Iniciar captura de audio
            self._recording_file = self.audio_capture.start_recording(
                duration=self.state_machine.timeout_recording
            )
            
        except Exception as e:
            logger.error(f"Error iniciando grabación: {e}")
            self.handle_error(f"Error de grabación: {e}")
    
    def stop_recording(self):
        """Detiene grabación y envía al backend"""
        logger.info("Deteniendo grabación...")
        
        try:
            # Guardar archivo
            self._recording_file = self.audio_capture.stop_recording()
            
            if not self._recording_file:
                raise Exception("No se grabó audio")
            
            # Transición a envío
            self.state_machine.transition_to(
                DeviceState.SENDING,
                reason="Grabación completada"
            )
            
            # Enviar al backend
            self.send_to_backend()
            
        except Exception as e:
            logger.error(f"Error deteniendo grabación: {e}")
            self.handle_error(f"Error guardando audio: {e}")
    
    def send_to_backend(self):
        """Envía audio al backend"""
        logger.info(f"Enviando {self._recording_file} al backend...")
        
        try:
            response = self.network_manager.send_audio(
                self._recording_file
            )
            
            if response and 'audio_url' in response:
                # Transición a descarga
                self.state_machine.transition_to(
                    DeviceState.PROCESSING,
                    reason="Respuesta recibida"
                )
                
                # Descargar y reproducir
                self.download_and_play(response['audio_url'])
            else:
                raise Exception("Respuesta inválida del backend")
                
        except Exception as e:
            logger.error(f"Error enviando al backend: {e}")
            self.handle_error(f"Error de red: {e}")
    
    def download_and_play(self, audio_url: str):
        """Descarga audio de respuesta y lo reproduce"""
        logger.info(f"Descargando {audio_url}...")
        
        try:
            self._response_audio_file = self.network_manager.download_audio(
                audio_url
            )
            
            if not self._response_audio_file:
                raise Exception("Descarga de audio fallida")
            
            # Transición a reproducción
            self.state_machine.transition_to(
                DeviceState.PLAYING,
                reason="Audio descargado"
            )
            
            # Reproducir
            self.audio_playback.play(self._response_audio_file)
            
            # Volver a IDLE cuando termine
            self.state_machine.transition_to(
                DeviceState.IDLE,
                reason="Reproducción completada"
            )
            
        except Exception as e:
            logger.error(f"Error descargando/reproduciendo: {e}")
            self.handle_error(f"Error de reproducción: {e}")
    
    def handle_error(self, error_message: str):
        """Maneja un error del sistema"""
        logger.error(f"ERROR: {error_message}")
        
        self.state_machine.transition_to(
            DeviceState.ERROR,
            reason=error_message
        )
        
        # Esperar 5 segundos y volver a IDLE
        time.sleep(5)
        
        self.state_machine.transition_to(
            DeviceState.IDLE,
            reason="Recuperación de error"
        )
    
    def check_system_health(self) -> bool:
        """
        Verifica la salud del sistema.
        Retorna True si está bien, False si hay error.
        """
        # Verificar conectividad de red
        if not self.network_manager.is_connected():
            logger.warning("Sin conexión de red")
            return False
        
        # Verificar timeout si está en estado time-sensitive
        if self.state_machine.check_timeout():
            self.handle_error("Timeout del sistema")
            return False
        
        return True


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    """Test básico de la máquina de estados"""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Mock de controladores para test
    class MockLEDController:
        def set_color(self, color):
            print(f"  LED: {color}")
    
    class MockButtonController:
        def on_press(self, callback):
            pass
    
    # Crear máquina de estados
    led = MockLEDController()
    btn = MockButtonController()
    
    state_machine = StateMachine(led, btn)
    
    # Registrar algunos callbacks
    def on_recording_enter():
        print("  [CALLBACK] Iniciando grabación...")
    
    def on_recording_exit():
        print("  [CALLBACK] Grabación finalizada")
    
    state_machine.register_callback(DeviceState.RECORDING, 'enter', on_recording_enter)
    state_machine.register_callback(DeviceState.RECORDING, 'exit', on_recording_exit)
    
    # Test de transiciones
    print("\n=== Test de Máquina de Estados ===\n")
    
    print("Estado actual:", state_machine.current_state.value)
    
    print("\nTransición: IDLE → RECORDING")
    state_machine.transition_to(DeviceState.RECORDING, reason="Test")
    
    time.sleep(1)
    
    print("\nTransición: RECORDING → SENDING")
    state_machine.transition_to(DeviceState.SENDING, reason="Test")
    
    time.sleep(1)
    
    print("\nTransición: SENDING → PROCESSING")
    state_machine.transition_to(DeviceState.PROCESSING, reason="Test")
    
    time.sleep(1)
    
    print("\nTransición: PROCESSING → PLAYING")
    state_machine.transition_to(DeviceState.PLAYING, reason="Test")
    
    time.sleep(1)
    
    print("\nTransición: PLAYING → IDLE")
    state_machine.transition_to(DeviceState.IDLE, reason="Test")
    
    print("\nInfo del estado:", state_machine.get_state_info())
    
    state_machine.shutdown()
    
    print("\n=== Test completado ===")
