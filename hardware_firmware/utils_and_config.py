"""
Módulos auxiliares:
- device_id_manager.py: Gestión de ID único del dispositivo
- logger_config.py: Configuración centralizada de logging
- config.py: Configuración por defecto
"""

import uuid
import os
import logging
import logging.handlers
from pathlib import Path


# ============================================================================
# DEVICE ID MANAGER
# ============================================================================

class DeviceIDManager:
    """
    Genera y persiste un ID único para el dispositivo.
    Se usa para identificar el dispositivo en el backend.
    """
    
    def __init__(self, id_file: str = '/home/pi/hardware-firmware/.device_id'):
        """
        Inicializa el gestor de Device ID.
        
        Args:
            id_file: Ruta del archivo donde se persiste el ID
        """
        self.id_file = id_file
        self._device_id = None
    
    def get_device_id(self) -> str:
        """
        Obtiene o genera el Device ID.
        
        Returns:
            ID único del dispositivo (UUID v4 como string)
        """
        if self._device_id:
            return self._device_id
        
        # Intentar leer del archivo
        if os.path.exists(self.id_file):
            try:
                with open(self.id_file, 'r') as f:
                    self._device_id = f.read().strip()
                    if self._device_id:
                        return self._device_id
            except Exception:
                pass
        
        # Generar nuevo ID si no existe
        self._device_id = str(uuid.uuid4())
        
        # Persistir en archivo
        try:
            os.makedirs(os.path.dirname(self.id_file), exist_ok=True)
            with open(self.id_file, 'w') as f:
                f.write(self._device_id)
        except Exception as e:
            print(f"Advertencia: No se pudo persistir Device ID: {e}")
        
        return self._device_id
    
    def reset_device_id(self):
        """
        Reinicia el Device ID (genera uno nuevo).
        Útil para factory reset.
        """
        self._device_id = str(uuid.uuid4())
        
        try:
            os.makedirs(os.path.dirname(self.id_file), exist_ok=True)
            with open(self.id_file, 'w') as f:
                f.write(self._device_id)
        except Exception as e:
            print(f"Error: No se pudo reiniciar Device ID: {e}")
        
        return self._device_id


# ============================================================================
# LOGGER CONFIG
# ============================================================================

class ColoredFormatter(logging.Formatter):
    """Formateador de logs con colores para consola"""
    
    # Códigos ANSI para colores
    COLORS = {
        'DEBUG': '\\033[36m',      # Cyan
        'INFO': '\\033[32m',       # Green
        'WARNING': '\\033[33m',    # Yellow
        'ERROR': '\\033[31m',      # Red
        'CRITICAL': '\\033[35m',   # Magenta
        'RESET': '\\033[0m',
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logging(log_file: str = None, 
                 log_level: str = 'INFO',
                 name: str = None) -> logging.Logger:
    """
    Configura el sistema de logging centralizado.
    
    Args:
        log_file: Ruta del archivo de log (None = solo consola)
        log_level: Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        name: Nombre del logger (None = root logger)
        
    Returns:
        Logger configurado
    """
    
    # Obtener logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Evitar handlers duplicados
    if logger.handlers:
        return logger
    
    # Formato
    format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Handler para consola (con colores)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_formatter = ColoredFormatter(format_str, datefmt=date_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo (si especificado)
    if log_file:
        try:
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            # Rotación automática de logs
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=5 * 1024 * 1024,  # 5 MB
                backupCount=5
            )
            file_handler.setLevel(getattr(logging, log_level.upper()))
            file_formatter = logging.Formatter(format_str, datefmt=date_format)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.error(f"Error configurando log file: {e}")
    
    return logger


# ============================================================================
# CONFIG DEFAULTS
# ============================================================================

class Config:
    """Configuración por defecto del dispositivo"""
    
    # Audio
    SAMPLE_RATE = 16000  # Hz
    CHANNELS = 1        # Mono
    AUDIO_CHUNK_SIZE = 1024
    MAX_RECORDING_SECONDS = 60
    
    # GPIO
    GPIO_BUTTON = 17
    GPIO_LED_RED = 27
    GPIO_LED_GREEN = 23
    GPIO_LED_BLUE = 24
    
    # Network
    BACKEND_URL = 'http://localhost:8000'
    BACKEND_TIMEOUT = 30
    MAX_RETRIES = 3
    RETRY_BASE_DELAY = 1.0
    
    # Device
    DEVICE_NAME = 'Animal Device'
    LOG_LEVEL = 'INFO'
    LOG_FILE = '/home/pi/hardware-firmware/logs/device.log'
    
    # Timeouts
    TIMEOUT_RECORDING = 60      # segundos
    TIMEOUT_SENDING = 30
    TIMEOUT_PROCESSING = 30
    TIMEOUT_PLAYING = 120
    
    # LED Colors (RGB 0.0-1.0)
    LED_COLOR_IDLE = (0, 0, 1)       # Azul
    LED_COLOR_RECORDING = (1, 0, 0)  # Rojo
    LED_COLOR_SENDING = (1, 0.5, 0)  # Naranja
    LED_COLOR_PROCESSING = (1, 1, 0) # Amarillo
    LED_COLOR_PLAYING = (0, 1, 0)    # Verde
    LED_COLOR_ERROR = (1, 0, 0)      # Rojo
    
    @classmethod
    def from_env(cls):
        """Crea configuración desde variables de entorno"""
        import os
        
        config = {}
        
        # Mapear variables de entorno a atributos de clase
        env_mapping = {
            'SAMPLE_RATE': 'sample_rate',
            'AUDIO_CHUNK_SIZE': 'audio_chunk_size',
            'MAX_RECORDING_SECONDS': 'max_recording_seconds',
            'GPIO_BUTTON': 'gpio_button',
            'GPIO_LED_RED': 'gpio_led_red',
            'GPIO_LED_GREEN': 'gpio_led_green',
            'GPIO_LED_BLUE': 'gpio_led_blue',
            'BACKEND_URL': 'backend_url',
            'BACKEND_TIMEOUT': 'backend_timeout',
            'DEVICE_NAME': 'device_name',
            'LOG_LEVEL': 'log_level',
            'LOG_FILE': 'log_file',
        }
        
        for env_var, config_key in env_mapping.items():
            if env_var in os.environ:
                value = os.environ[env_var]
                
                # Intentar convertir a tipo apropiado
                if config_key.startswith('gpio_') or config_key in ['sample_rate', 'audio_chunk_size', 'max_recording_seconds', 'backend_timeout']:
                    try:
                        config[config_key] = int(value)
                    except ValueError:
                        config[config_key] = value
                else:
                    config[config_key] = value
        
        return config
    
    @classmethod
    def to_dict(cls):
        """Convierte configuración a diccionario"""
        return {k: v for k, v in cls.__dict__.items() 
                if not k.startswith('_') and k.isupper()}


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    """Test de módulos auxiliares"""
    
    print("\\n=== Test de Módulos Auxiliares ===\\n")
    
    # Test Device ID
    print("Test Device ID Manager:")
    id_manager = DeviceIDManager()
    device_id = id_manager.get_device_id()
    print(f"  Device ID: {device_id}")
    
    # Verificar que es consistente
    device_id_2 = id_manager.get_device_id()
    print(f"  Consistencia: {device_id == device_id_2}")
    
    # Test Logging
    print("\\nTest Logger:")
    logger = setup_logging(
        log_file='/tmp/test.log',
        log_level='DEBUG'
    )
    
    logger.debug("Este es un mensaje de DEBUG")
    logger.info("Este es un mensaje de INFO")
    logger.warning("Este es un mensaje de WARNING")
    logger.error("Este es un mensaje de ERROR")
    
    # Test Config
    print("\\nTest Config:")
    config = Config.to_dict()
    for key, value in list(config.items())[:5]:
        print(f"  {key}: {value}")
    print(f"  ... ({len(config)} configuraciones totales)")
    
    print("\\n=== Test completado ===\\n")
