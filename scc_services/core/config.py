import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # --- POSTGRES ---
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "SCC"
    POSTGRES_HOST: str = "db_postgres" 
    POSTGRES_PORT: int = 5432
    DB_SCHEMA: str = "scc_user, public"

    # --- SEGURIDAD ---
    SECRET_KEY: str = "nu3v0s1st3m4d3calc8l0d3c0m1c10n3s_d1g1_s3cr3et_k3y_2026"
    ALGORITHM: str = "HS256"

    # --- ORACLE ---
    ORA_CRM_USER: Optional[str] = None
    ORA_CRM_PASS: Optional[str] = None
    ORA_CRM_DSN: Optional[str] = None
    ORA_SQL_USER: Optional[str] = None
    ORA_SQL_PASS: Optional[str] = None
    ORA_SQL_DSN: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra="ignore"
    )

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()