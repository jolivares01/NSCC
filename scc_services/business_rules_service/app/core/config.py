import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional

# --- BÚSQUEDA DINÁMICA DEL .env ---
def find_env_file():
    """Busca el archivo .env en el directorio actual o padres hasta encontrarlo."""
    current_dir = Path(__file__).resolve().parent
    for _ in range(6):  # Busca hasta 6 niveles arriba
        potential_path = current_dir / ".env"
        if potential_path.exists():
            return potential_path
        current_dir = current_dir.parent
    return None

ENV_PATH = find_env_file()

print(f"\n--- DEBUG CONFIG ---")
print(f"Buscando archivo .env en: {ENV_PATH}")
print(f"¿El archivo existe?: {ENV_PATH is not None}")
print(f"--------------------\n")

class Settings(BaseSettings):
    # --- POSTGRES (Común a todos) ---
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "SCC"
    #POSTGRES_HOST: str = "localhost"
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "db_postgres")
    POSTGRES_PORT: str = "5432"
    DB_SCHEMA: str = "scc_user, public"

    # --- SEGURIDAD (Para validar tokens en cada servicio) ---
    SECRET_KEY: str = "nu3v0s1st3m4d3calc8l0d3c0m1c10n3s_d1g1_s3cr3et_k3y_2026"
    ALGORITHM: str = "HS256"

    # --- ORACLE (Cambiamos str por Optional[str]) ---
    # Esto permite que el valor sea None si no existe en el .env
    ORA_USER: Optional[str] = None
    ORA_PASS: Optional[str] = None
    ORA_DSN: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding='utf-8',
        extra="ignore"
    )

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()