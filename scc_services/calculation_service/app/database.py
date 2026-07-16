import asyncpg
import oracledb
from fastapi import Request
from scc_services.core.config import settings

# --- MUNDO POSTGRES (Async) ---
async def create_db_pool(app):
    app.state.db_pool = await asyncpg.create_pool(
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        database=settings.POSTGRES_DB,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        server_settings={'search_path': settings.DB_SCHEMA},
        min_size=1,
        max_size=30,
        command_timeout=300
    )

async def close_db_pool(app):
    await app.state.db_pool.close()

def get_db_pool(request: Request) -> asyncpg.Pool:
    return request.app.state.db_pool

# --- MUNDO ORACLE (Sync/Thick/Thin) ---
def get_oracle_connection(target: str = "CRMGOLD"):
    """
    Retorna una conexión a Oracle basada en el target.
    target: 'CRMGOLD' o 'SQL360'
    """
    if target == "CRMGOLD":
        return oracledb.connect(
            user=settings.ORA_CRM_USER,
            password=settings.ORA_CRM_PASS,
            dsn=settings.ORA_CRM_DSN
        )
    else:
        return oracledb.connect(
            user=settings.ORA_SQL_USER,
            password=settings.ORA_SQL_PASS,
            dsn=settings.ORA_SQL_DSN
        )