import asyncpg
import os
from fastapi import Request

# Variable global para el shutdown (opcional si usas app.state)
db_pool = None

# Crear el pool de conexiones
async def create_db_pool(app):
    global db_pool
    db_pool = await asyncpg.create_pool(
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "Jaoc2645796321++"),
        database=os.getenv("POSTGRES_DB", "SCC"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        server_settings={'search_path': 'scc_user, public'}
    )
    app.state.db_pool = db_pool

# Cerrar el pool
async def close_db_pool(app):
    await app.state.db_pool.close()

# ✅ NUEVA FUNCIÓN GETTER usando Request
def get_db_pool(request: Request) -> asyncpg.Pool:
    return request.app.state.db_pool