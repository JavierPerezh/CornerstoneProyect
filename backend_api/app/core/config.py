import os
from pathlib import Path
from dotenv import load_dotenv

# Localizar la raiz del proyecto (backend_api/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Cargar variables desde el archivo .env
load_dotenv(os.path.join(BASE_DIR, ".env"))

class Settings:
    """
    Configuracion centralizada de la aplicacion.
    Carga variables de entorno y define rutas estaticas del sistema.
    """
    PROJECT_NAME: str = "Cornerstone Proyecto - MACC"
    VERSION: str = "1.0.0"
    
    # Configuracion de API Externa
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    
    # Rutas del Sistema de Archivos
    APP_DIR: Path = BASE_DIR / "app"
    MODELS_DIR: Path = APP_DIR / "models" / "weights"
    TRAINING_DIR: Path = APP_DIR / "training"
    
    # Nombre del archivo de parametros entrenados
    MODEL_PARAMS_FILE: str = "parametros_finales.json"
    
    # Hiperparametros por defecto para el modelo matematico
    DEFAULT_LEARNING_RATE: float = 0.1
    DEFAULT_EPOCHS: int = 1500

    @property
    def model_path(self) -> Path:
        """Retorna la ruta absoluta al archivo de pesos del modelo."""
        return self.MODELS_DIR / self.MODEL_PARAMS_FILE

    def validate_config(self):
        """Verifica que las credenciales criticas esten presentes."""
        if not self.GROQ_API_KEY:
            raise ValueError("Error: GROQ_API_KEY no encontrada en el entorno.")
        print(f"Configuracion cargada exitosamente para: {self.PROJECT_NAME}")

# Instancia unica para ser importada en el resto del sistema
settings = Settings()

if __name__ == "__main__":
    # Prueba rapida de carga
    try:
        settings.validate_config()
        print(f"Ruta del modelo: {settings.model_path}")
    except Exception as e:
        print(e)