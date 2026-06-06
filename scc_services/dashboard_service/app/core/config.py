import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

# 1. Ruta dinámica para el USER SERVICE
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

# --- BLOQUE DE DEPURACIÓN ESPECÍFICO ---
print(f"\n--- DEBUG CONFIG: USER_SERVICE ---")
print(f"Buscando archivo .env en: {ENV_PATH}")
print(f"¿El archivo existe?: {ENV_PATH.exists()}")
print(f"----------------------------------\n")

class Settings(BaseSettings):
    # --- CONEXIÓN BASE DE DATOS ---
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "SCC"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    DB_SCHEMA: str = "scc_user, public"

    # --- SEGURIDAD ---
    # Necesaria para validar que el administrador tenga sesión activa al crear usuarios
    SECRET_KEY: str = "nu3v0s1st3m4d3calc8l0d3c0m1c10n3s_d1g1_s3cr3et_k3y_2026"
    ALGORITHM: str = "HS256"

    # Configuración del archivo .env
    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding='utf-8',
        extra="ignore"
    )

@lru_cache()
def get_settings():
    """Carga la configuración una sola vez en memoria"""
    return Settings()

settings = get_settings()