from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/posparto_db"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
