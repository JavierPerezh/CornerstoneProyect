"""Configuración central de la aplicación."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Variables de entorno del proyecto."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    DATABASE_URL: str
    GROQ_API_KEY: str
    OPENAI_API_KEY: str
    DEVICE_API_KEY_SECRET: str
    JWT_SECRET: str
    JWT_EXPIRE_DAYS: int = 30
    ENVIRONMENT: str = "development"
    STATIC_AUDIO_DIR: str = "static/audio"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Devuelve una instancia cacheada de configuración."""

    return Settings()
