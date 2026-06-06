from fastapi import APIRouter, HTTPException, Request, Query
from .models import ClaimCreate, InteractionCreate
from .database import get_db_pool
from datetime import datetime
from typing import Optional
# --- IMPORTACIÓN DEL CONFIGURADOR DE LOGS ---
from api_gateway.utils.logger_config import setup_logger

# Inicialización del logger para este servicio
log = setup_logger("CLAIMS-SERVICE")

router = APIRouter()

# --- PARA EL AGENTE (ROL_0002) ---

@router.post("/create-claim")
async def create_claim(data: ClaimCreate, request: Request):
    db_pool = get_db_pool(request)
    log.debug(f"Petición para crear reclamo. Agente: {data.agente} | Contenido: {data.desc_claims[:50]}...")
    
    query = """
        INSERT INTO scc_user.claims (agente, desc_claims) 
        VALUES ($1, $2) 
        RETURNING id_inc_claims
    """
    try:
        async with db_pool.acquire() as conn:
            id_inc = await conn.fetchval(query, data.agente, data.desc_claims)
            log.info(f"Reclamo creado exitosamente. ID Generado: {id_inc} | Por Agente: {data.agente}")
            return {"estado": "EXITO", "id_inc_claims": id_inc}
    except Exception as e:
        log.error(f"Error al crear reclamo para el agente {data.agente}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno al registrar el reclamo")

# --- PARA AMBOS ROLES (LISTAR ABIERTOS) ---

@router.get("/list-open")
async def list_open(username: str, id_rol: str, request: Request):
    db_pool = get_db_pool(request)
    log.debug(f"Solicitud de lista de reclamos abiertos. Usuario: {username} | Rol: {id_rol}")
    
    # Si es Admin (ROL_0001) ve todos, si es Agente (ROL_0002) ve los suyos
    if id_rol == "ROL_0001":
        query = "SELECT * FROM scc_user.claims WHERE status = 'ABIERTO' ORDER BY created_dt DESC"
        params = []
    else:
        query = "SELECT * FROM scc_user.claims WHERE agente = $1 AND status = 'ABIERTO' ORDER BY created_dt DESC"
        params = [username]

    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            log.info(f"Lista de abiertos cargada. Registros: {len(rows)} para el rol {id_rol}")
            return [dict(row) for row in rows]
    except Exception as e:
        log.error(f"Error al listar reclamos abiertos para {username}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al consultar reclamos")

# --- PARA EL ADMINISTRADOR (RESPONDER) ---

@router.post("/respond-claim")
async def respond_claim(data: InteractionCreate, request: Request):
    db_pool = get_db_pool(request)
    log.debug(f"Admin {data.admin_user} respondiendo al ticket ID: {data.id_inc_claims}")
    
    try:
        async with db_pool.acquire() as connection:
            async with connection.transaction():
                # 1. Registro de la interacción
                await connection.execute(
                    """
                    INSERT INTO scc_user.interaction_claims 
                    (id_inc_claims, user_response_message, created_dt, change_dt, created_who, changed_who) 
                    VALUES ($1, $2, NOW(), NOW(), $3, $3)
                    """,
                    data.id_inc_claims, 
                    data.user_response_message, 
                    data.admin_user 
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
                
            log.info(f"Ticket {data.id_inc_claims} marcado como ATENDIDO por {data.admin_user}")
            return {"estado": "EXITO", "mensaje": "Respuesta registrada correctamente"}
    except Exception as e:
        log.error(f"Fallo en la transacción de respuesta para ticket {data.id_inc_claims}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al procesar la respuesta en base de datos")

# --- NOTIFICACIÓN DESDE EL NAVBAR ---

@router.get("/notifications-count")
async def get_notifications_count(id_rol: str, username: str, request: Request):
    db_pool = get_db_pool(request)
    # DEBUG muy sutil para no saturar ya que este se llama cada 30 segundos
    log.debug(f"Polling de notificaciones: {username} ({id_rol})")
    
    try:
        async with db_pool.acquire() as conn:
            if id_rol == "ROL_0001":
                query = "SELECT COUNT(*) FROM scc_user.claims WHERE status = 'ABIERTO'"
                count = await conn.fetchval(query)
            else:
                query = "SELECT COUNT(*) FROM scc_user.claims WHERE agente = $1 AND status = 'ATENDIDO'"
                count = await conn.fetchval(query, username)
                
            return {"count": count}
    except Exception as e:
        log.error(f"Error en el conteo de notificaciones para {username}: {str(e)}")
        # No lanzamos excepción aquí para no romper el frontend durante el polling
        return {"count": 0}

# --- CONSULTA DE ATENDIDOS POR MES (RANGO DE FECHAS) ---

@router.get("/list-attended")
async def list_attended(id_rol: str, start_date: str, end_date: str, request: Request, username: Optional[str] = None):
    db_pool = get_db_pool(request)
    log.debug(f"Consulta de históricos. Rango: {start_date} al {end_date} | Solicitado por: {username}")
    
    query = """
        SELECT c.*, i.user_response_message 
        FROM scc_user.claims c
        LEFT JOIN scc_user.interaction_claims i ON c.id_inc_claims = i.id_inc_claims
        WHERE c.status = 'ATENDIDO' 
          AND c.created_dt BETWEEN $1 AND $2
    """
    try:
        params = [datetime.fromisoformat(start_date), datetime.fromisoformat(end_date)]

        if id_rol == "ROL_0002":
            query += " AND c.agente = $3"
            params.append(username)

        async with db_pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            log.info(f"Histórico cargado: {len(rows)} registros atendidos encontrados.")
            return [dict(row) for row in rows]
    except Exception as e:
        log.error(f"Error al consultar lista de atendidos: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al obtener históricos")