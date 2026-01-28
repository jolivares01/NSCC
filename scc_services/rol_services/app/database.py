import asyncpg
import os
from fastapi import Request

async def create_db_pool(app):
    app.state.db_pool = await asyncpg.create_pool(
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "Jaoc2645796321++"),
        database=os.getenv("POSTGRES_DB", "SCC"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        server_settings={'search_path': 'scc_user, public'}
    )

async def close_db_pool(app):
    await app.state.db_pool.close()

def get_db_pool(request: Request) -> asyncpg.Pool:
    return request.app.state.db_pool