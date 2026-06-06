import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

# 1. Obtenemos la ruta absoluta de la carpeta 'report_service'
# Path(__file__) es .../app/core/config.py
# .parent -> .../app/core/
# .parent.parent -> .../app/
# .parent.parent.parent -> .../report_service/
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

# --- BLOQUE DE DEPURACIÓN (Míralo en la consola al arrancar) ---
print(f"\n--- DEBUG CONFIG ---")
print(f"Buscando archivo .env en: {ENV_PATH}")
print(f"¿El archivo existe?: {ENV_PATH.exists()}")
print(f"--------------------\n")
# -------------------------------------------------------------

class Settings(BaseSettings):
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "SCC"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    DB_SCHEMA: str = "scc_user, public"

    # Configuración del archivo .env
    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding='utf-8',
        extra="ignore"
    )

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()