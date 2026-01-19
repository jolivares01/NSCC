from fastapi import APIRouter, HTTPException, Request, Query
from .models import ClaimCreate, InteractionCreate
from .database import get_db_pool
from datetime import datetime
from typing import Optional

router = APIRouter()

# --- PARA EL AGENTE (ROL_0002) ---

@router.post("/create-claim")
async def create_claim(data: ClaimCreate, request: Request):
    db_pool = get_db_pool(request)
    query = """
        INSERT INTO scc_user.claims (agente, desc_claims) 
        VALUES ($1, $2) 
        RETURNING id_inc_claims
    """
    async with db_pool.acquire() as conn:
        id_inc = await conn.fetchval(query, data.agente, data.desc_claims)
        return {"estado": "EXITO", "id_inc_claims": id_inc}

# --- PARA AMBOS ROLES (LISTAR ABIERTOS) ---

@router.get("/list-open")
async def list_open(username: str, id_rol: str, request: Request):
    db_pool = get_db_pool(request)
    
    # Si es Admin (ROL_0001) ve todos, si es Agente (ROL_0002) ve los suyos
    if id_rol == "ROL_0001":
        query = "SELECT * FROM scc_user.claims WHERE status = 'ABIERTO' ORDER BY created_dt DESC"
        params = []
    else:
        query = "SELECT * FROM scc_user.claims WHERE agente = $1 AND status = 'ABIERTO' ORDER BY created_dt DESC"
        params = [username]

    async with db_pool.acquire() as conn:
        rows = await conn.fetch(query, *params)
        return [dict(row) for row in rows]

# --- PARA EL ADMINISTRADOR (RESPONDER) ---

@router.post("/respond-claim")
async def respond_claim(data: InteractionCreate, request: Request):
    db_pool = get_db_pool(request)
    async with db_pool.acquire() as connection:
        async with connection.transaction():
            # Guardamos el login del admin en created_who y changed_who
            await connection.execute(
                """
                INSERT INTO scc_user.interaction_claims 
                (id_inc_claims, user_response_message, created_dt, change_dt, created_who, changed_who) 
                VALUES ($1, $2, NOW(), NOW(), $3, $3)
                """,
                data.id_inc_claims, 
                data.user_response_message, 
                data.admin_user # Este es el login que viene del frontend
            )
            
            # 2. Actualización de la tabla maestra claims
            await connection.execute(
                """
                UPDATE scc_user.claims 
                SET status = 'ATENDIDO', 
                    change_dt = NOW(),
                    changed_who = $2
                WHERE id_inc_claims = $1
                """,
                data.id_inc_claims, 
                data.admin_user
            )
            
        return {"estado": "EXITO", "mensaje": "Respuesta y auditoría registradas correctamente"}

# --- NOTIFICACIÓN DESDE EL NAVBAR ---

@router.get("/notifications-count")
async def get_notifications_count(id_rol: str, username: str, request: Request):
    db_pool = get_db_pool(request)
    async with db_pool.acquire() as conn:
        if id_rol == "ROL_0001":
            # Cuenta todos los tickets abiertos para el Admin
            query = "SELECT COUNT(*) FROM scc_user.claims WHERE status = 'ABIERTO'"
            count = await conn.fetchval(query)
        else:
            # Cuenta tickets atendidos específicos para el Agente
            query = "SELECT COUNT(*) FROM scc_user.claims WHERE agente = $1 AND status = 'ATENDIDO'"
            count = await conn.fetchval(query, username)
            
        return {"count": count}

# --- CONSULTA DE ATENDIDOS POR MES (RANGO DE FECHAS) ---

@router.get("/list-attended")
async def list_attended(id_rol: str, start_date: str, end_date: str, request: Request, username: Optional[str] = None):
    db_pool = get_db_pool(request)
    
    # Consulta con JOIN para traer la respuesta del administrador
    query = """
        SELECT c.*, i.user_response_message 
        FROM scc_user.claims c
        LEFT JOIN scc_user.interaction_claims i ON c.id_inc_claims = i.id_inc_claims
        WHERE c.status = 'ATENDIDO' 
          AND c.created_dt BETWEEN $1 AND $2
    """
    params = [datetime.fromisoformat(start_date), datetime.fromisoformat(end_date)]

    if id_rol == "ROL_0002":
        query += " AND c.agente = $3"
        params.append(username)

    async with db_pool.acquire() as conn:
        rows = await conn.fetch(query, *params)
        return [dict(row) for row in rows]