import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

# 1. Ruta dinámica para el CALCULATION SERVICE
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

# --- BLOQUE DE DEPURACIÓN PARA VALIDAR EL .ENV ---
print(f"\n--- DEBUG CONFIG: {BASE_DIR.name.upper()} ---")
print(f"Buscando archivo .env en: {ENV_PATH}")
print(f"¿El archivo existe?: {ENV_PATH.exists()}")
# Imprimimos una confirmación visual de que las variables críticas están mapeadas
if ENV_PATH.exists():
    print("Estado: Cargando configuración híbrida (Postgres + Oracle)...")
print(f"------------------------------------------\n")

class Settings(BaseSettings):
    # --- POSTGRES (Reglas de Negocio) ---
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str = "5432"
    DB_SCHEMA: str = "scc_user, public"

    # --- SEGURIDAD ---
    SECRET_KEY: str = "nu3v0s1st3m4d3calc8l0d3c0m1c10n3s_d1g1_s3cr3et_k3y_2026"
    ALGORITHM: str = "HS256"

    # --- ORACLE 1: CRMGOLD ---
    ORA_CRM_USER: str
    ORA_CRM_PASS: str
    ORA_CRM_DSN: str

    # --- ORACLE 2: SQL360 ---
    ORA_SQL_USER: str
    ORA_SQL_PASS: str
    ORA_SQL_DSN: str

    # Configuración de Pydantic para leer el archivo .env
    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding='utf-8',
        extra="ignore"
    )

@lru_cache()
def get_settings():
    """Carga la configuración una sola vez y la mantiene en caché para optimizar los cálculos"""
    return Settings()

# Instancia global
settings = get_settings()
print(f"DEBUG CLAVE: La clave cargada tiene {len(settings.ORA_SQL_PASS)} caracteres.")
if settings.ORA_SQL_PASS.startswith("hola"):
    print("DEBUG CLAVE: Comienza correctamente con 'hola'")