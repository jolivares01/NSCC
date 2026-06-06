from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):
    # El Gateway solo necesita saber la llave para el logging de auditoría
    SECRET_KEY: str = "nu3v0s1st3m4d3calc8l0d3c0m1c10n3s_d1g1_s3cr3et_k3y_2026"
    ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding='utf-8',
        extra="ignore"
    )

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()