import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- Localización de la raíz del proyecto ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(os.path.join(BASE_DIR, ".env"))

class Settings(BaseSettings):
    """Configuración centralizada de la aplicación (Variables de entorno y rutas)."""

    # Configuración de Pydantic para el archivo .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Información General ---
    PROJECT_NAME: str = "Cornerstone Proyect"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    # --- Credenciales y API Keys ---
    DATABASE_URL: str
    GROQ_API_KEY: str
    OPENAI_API_KEY: Optional[str] = None
    DEVICE_API_KEY_SECRET: str
    JWT_SECRET: str
    JWT_EXPIRE_DAYS: int = 30

    # --- Rutas del Sistema de Archivos ---
    STATIC_AUDIO_DIR: str = "static/audio"
    APP_DIR: Path = BASE_DIR / "app"
    MODELS_DIR: Path = BASE_DIR / "app" / "models" / "weights"
    TRAINING_DIR: Path = BASE_DIR / "app" / "training"
    
    # --- Configuración del Modelo ---
    MODEL_PARAMS_FILE: str = "parametros_finales.json"
    DEFAULT_LEARNING_RATE: float = 0.1
    DEFAULT_EPOCHS: int = 1500

    @property
    def model_path(self) -> Path:
        """Retorna la ruta absoluta al archivo de pesos del modelo."""
        return self.MODELS_DIR / self.MODEL_PARAMS_FILE

    def validate_config(self):
        """Verifica que las credenciales críticas estén presentes."""
        if not self.GROQ_API_KEY:
            raise ValueError("Error: GROQ_API_KEY no encontrada en el entorno.")
        print(f"✅ Configuración cargada exitosamente para: {self.PROJECT_NAME}")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Devuelve una instancia cacheada de la configuración."""
    return Settings()

# Instancia única para uso global
settings = get_settings()

if __name__ == "__main__":
    # Prueba rápida de carga
    try:
        settings.validate_config()
        print(f"Modo: {settings.ENVIRONMENT}")
        print(f"Ruta del modelo: {settings.model_path}")
        print(f"Directorio de entrenamiento: {settings.TRAINING_DIR}")
    except Exception as e:
        print(f"❌ Error en la configuración: {e}")