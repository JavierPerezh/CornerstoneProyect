"""
main.py - Punto de entrada del firmware Animal Device

Orquesta todos los módulos:
- GPIO (LED y botón)
- Audio (captura y reproducción)
- Red (HTTP y WiFi)
- Máquina de estados
"""

import signal
import sys
import logging
import os
from dotenv import load_dotenv
import time
from pathlib import Path

# Importar módulos del proyecto
from gpio_manager import GPIOManager
from audio_modules import AudioCapture, AudioPlayback
from network_manager import NetworkManager
from state_machine import StateMachine, StateMachineManager, DeviceState
from device_id_manager import DeviceIDManager
from logger_config import setup_logging

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logger = setup_logging(
    log_file=os.getenv('LOG_FILE', '/home/pi/hardware-firmware/logs/device.log'),
    log_level=os.getenv('LOG_LEVEL', 'INFO')
)

logger.info("=" * 80)
logger.info("INICIANDO ANIMAL DEVICE FIRMWARE")
logger.info("=" * 80)


# ============================================================================
# CLASE PRINCIPAL
# ============================================================================

class AnimalDevice:
    """
    Controlador principal del dispositivo.
    Coordina todos los subsistemas.
    """
    
    def __init__(self):
        """Inicializa el dispositivo"""
        
        # Configuración centralizada
        self.config = {
            # Audio
            'sample_rate': int(os.getenv('SAMPLE_RATE', 16000)),
            'channels': 1,
            'chunk_size': int(os.getenv('AUDIO_CHUNK_SIZE', 1024)),
            
            # GPIO
            'gpio_button': int(os.getenv('GPIO_BUTTON', 17)),
            'gpio_led_red': int(os.getenv('GPIO_LED_RED', 27)),
            'gpio_led_green': int(os.getenv('GPIO_LED_GREEN', 23)),
            'gpio_led_blue': int(os.getenv('GPIO_LED_BLUE', 24)),
            
            # Network
            'backend_url': os.getenv('BACKEND_URL', 'http://localhost:8000'),
            'backend_timeout': int(os.getenv('BACKEND_TIMEOUT', 30)),
            'max_retries': 3,
            'retry_base_delay': 1.0,
            
            # Device
            'device_name': os.getenv('DEVICE_NAME', 'Animal Device'),
            'max_recording_seconds': int(os.getenv('MAX_RECORDING_SECONDS', 60)),
        }
        
        # Obtener ID único del dispositivo
        id_manager = DeviceIDManager('/home/pi/hardware-firmware/.device_id')
        self.device_id = id_manager.get_device_id()
        
        logger.info(f"Device ID: {self.device_id}")
        logger.info(f"Device Name: {self.config['device_name']}")
        logger.info(f"Backend URL: {self.config['backend_url']}")
        
        # Inicializar módulos
        logger.info("Inicializando módulos...")
        
        try:
            # GPIO
            self.gpio_manager = GPIOManager(self.config)
            
            # Audio
            self.audio_capture = AudioCapture(self.config)
            self.audio_playback = AudioPlayback(self.config)
            
            # Network
            self.network_manager = NetworkManager(self.config, self.device_id)
            
            # State Machine
            self.state_machine = StateMachine(
                self.gpio_manager.led,
                self.gpio_manager.button
            )
            
            # State Machine Manager
            self.state_manager = StateMachineManager(
                self.state_machine,
                self.audio_capture,
                self.audio_playback,
                self.network_manager
            )
            
            logger.info("Todos los módulos inicializados correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando módulos: {e}")
            raise
    
    def startup(self):
        """Inicia el dispositivo"""
        logger.info("Iniciando dispositivo...")
        
        try:
            # Registrar handlers de GPIO
            self.gpio_manager.startup(
                on_button_press=self.state_manager.on_button_pressed,
                on_button_release=self.state_manager.on_button_pressed  # Ambos eventos disparan la acción
            )
            
            # Transición a IDLE
            self.state_machine.transition_to(DeviceState.IDLE, reason="Startup")
            
            logger.info("Dispositivo listo")
            logger.info(f"Presiona el botón en GPIO {self.config['gpio_button']} para comenzar")
            
        except Exception as e:
            logger.error(f"Error iniciando dispositivo: {e}")
            raise
    
    def run(self):
        """Loop principal"""
        logger.info("Iniciando loop principal...")
        
        try:
            # Verificación periódica de salud
            last_health_check = time.time()
            health_check_interval = 30  # segundos
            
            while True:
                # Verificar salud del sistema cada 30 segundos
                current_time = time.time()
                if current_time - last_health_check > health_check_interval:
                    if not self.state_manager.check_system_health():
                        logger.warning("Sistema no saludable")
                    last_health_check = current_time
                
                # Pequeña pausa para no monopolizar CPU
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            logger.info("Interrupción por usuario")
        except Exception as e:
            logger.error(f"Error en loop principal: {e}")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Apaga el dispositivo de forma ordenada"""
        logger.info("Apagando dispositivo...")
        
        try:
            # Detener máquina de estados
            if hasattr(self, 'state_machine'):
                self.state_machine.shutdown()
            
            # Limpiar GPIO
            if hasattr(self, 'gpio_manager'):
                self.gpio_manager.shutdown()
            
            # Limpiar audio
            if hasattr(self, 'audio_capture'):
                self.audio_capture.cleanup()
            if hasattr(self, 'audio_playback'):
                self.audio_playback.cleanup()
            
            # Limpiar red
            if hasattr(self, 'network_manager'):
                self.network_manager.cleanup()
            
            logger.info("Dispositivo apagado correctamente")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"Error durante apagado: {e}")
    
    def handle_signal(self, signum, frame):
        """Handler para señales del sistema"""
        logger.info(f"Recibida señal {signum}")
        sys.exit(0)


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

def main():
    """Función principal"""
    
    # Crear dispositivo
    device = AnimalDevice()
    
    # Registrar handlers de señales
    signal.signal(signal.SIGINT, device.handle_signal)
    signal.signal(signal.SIGTERM, device.handle_signal)
    
    # Startup
    device.startup()
    
    # Esperar conexión de red (con timeout)
    logger.info("Verificando conectividad de red...")
    if device.network_manager.wait_for_connection(max_wait=30):
        logger.info("Dispositivo conectado a internet")
        
        # Enviar información del dispositivo
        device.network_manager.send_device_info()
    else:
        logger.warning("Sin conexión a internet, operando en modo local")
    
    # Loop principal
    device.run()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.critical(f"Error crítico: {e}", exc_info=True)
        sys.exit(1)
