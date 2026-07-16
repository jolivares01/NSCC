import asyncpg
from fastapi import Request
from scc_services.core.config import settings
# Variable global para el shutdown
db_pool = None

async def create_db_pool(app):
    global db_pool
    db_pool = await asyncpg.create_pool(
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        database=settings.POSTGRES_DB,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        server_settings={'search_path': settings.DB_SCHEMA}
    )
    app.state.db_pool = db_pool

async def close_db_pool(app):
    if hasattr(app.state, 'db_pool'):
        await app.state.db_pool.close()

def get_db_pool(request: Request) -> asyncpg.Pool:
    return request.app.state.db_pool