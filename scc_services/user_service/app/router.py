from fastapi import APIRouter, HTTPException, Query, Request
from .models import RegistroUsuario, ActualizarUsuario
from .database import get_db_pool
# --- IMPORTACIÓN DEL CONFIGURADOR DE LOGS ---
from api_gateway.utils.logger_config import setup_logger

# Inicialización del logger específico para Gestión de Usuarios
log = setup_logger("USER-SERVICE")

router = APIRouter()

#  NUEVOS ENDPOINTS PARA DESPLEGABLES (MAESTROS) 

@router.get("/maestros/tipos-usuario")
async def obtener_tipos_usuario(request: Request):
    """Retorna id_type y description de scc_user.user_type"""
    db_pool = get_db_pool(request)
    log.debug("Consultando catálogo de tipos de usuario.")
    query = "SELECT id_type, description FROM scc_user.user_type ORDER BY id_type;"
    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [dict(r) for r in rows]
    except Exception as e:
        log.error(f"Error al obtener tipos de usuario: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error en catálogo")

@router.get("/maestros/canales")
async def obtener_canales(request: Request):
    db_pool = get_db_pool(request)
    log.debug("Consultando catálogo de canales.")
    sql_query = "SELECT id_channel, description FROM scc_user.user_channel ORDER BY id_channel;"
    try:
        async with db_pool.acquire() as conn:
            canales = await conn.fetch(sql_query)
            return [dict(c) for c in canales]
    except Exception as e:
        log.error(f"Error al obtener canales: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error en catálogo")

#  REGISTRO DE USUARIO ACTUALIZADO 

@router.post("/registrar-usuario")
async def registrar_usuario_endpoint(data: RegistroUsuario, request: Request):
    db_pool = get_db_pool(request)
    
    log.info(f"REGISTRO: Iniciando proceso para usuario '{data.username}' solicitado por '{data.createdBy}'")
    
    sql_query = "SELECT scc_user.sp_registrar_usuario($1, $2, $3, $4, $5, $6, $7, $8);"
    
    v_user_type = data.user_type if data.origin_type == 'EXTERNO' else None
    
    params = (
        data.region, 
        data.localidad, 
        data.username, 
        data.rol, 
        data.createdBy,
        data.origin_type,
        v_user_type,
        data.id_channel
    )

    log.debug(f"Parámetros SP registrar_usuario: {params}")

    try:
        async with db_pool.acquire() as connection:
            resultado_db = await connection.fetchval(sql_query, *params)
            
            if not resultado_db.startswith("EXITO"):
                log.warning(f"REGISTRO FALLIDO: La DB devolvió: {resultado_db} para usuario {data.username}")
                raise HTTPException(status_code=400, detail={"estado": "ERROR", "mensaje": resultado_db})
            
            log.info(f"REGISTRO EXITOSO: Usuario '{data.username}' creado correctamente.")
            return {"estado": "EXITO", "mensaje": resultado_db}
            
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        log.error(f"ERROR CRÍTICO en registro de usuario {data.username}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"mensaje": "Error interno del servidor"})

# CONSULTA PREVIA DE LOCALIDAD

@router.get("/maestros/localidades-por-region/{region_id}")
async def obtener_localidades_por_region(region_id: int, request: Request):
    db_pool = get_db_pool(request)
    log.debug(f"Filtrando localidades para región ID: {region_id}")
    sql_query = """
        SELECT id_location, display_value 
        FROM scc_user.location 
        WHERE id_region = $1 
        ORDER BY display_value;
    """
    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(sql_query, region_id)
            return [dict(r) for r in rows]
    except Exception as e:
        log.error(f"Error filtrando localidades para región {region_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error en consulta")

# VISTA PREVIA DE USUARIOS
@router.get("/usuarios-vista-previa")
async def obtener_usuarios_vista_previa(request: Request, search: str = ""):
    db_pool = get_db_pool(request)
    
    if not search or search.strip() == "":
        log.warning("Búsqueda de vista previa solicitada sin término de búsqueda.")
        raise HTTPException(
            status_code=400, 
            detail={"mensaje": "Debe proporcionar un usuario para buscar"}
        )
    
    search_term = search.strip()
    log.debug(f"Vista previa solicitada para: {search_term}")
    
    sql_query = """
        SELECT
            u.username AS "usuario",
            r.display_value AS "region",
            l.display_value AS "localidad",
            CASE 
                WHEN u.inactive_dt IS NULL THEN 'Activo' 
                ELSE 'Inactivo' 
            END AS "estado",
            COALESCE(STRING_AGG(rol_t.rol_name, ', '), 'Sin roles asignados') AS "roles_asignados",
            u.inactive_dt
        FROM SCC_USER.users u
        LEFT JOIN SCC_USER.region r ON u.id_region = r.id_region
        LEFT JOIN SCC_USER.location l ON u.id_location = l.id_location
        LEFT JOIN SCC_USER.user_rol ur ON u.username = ur.username
        LEFT JOIN SCC_USER.rol rol_t ON ur.id_rol = rol_t.id_rol
        WHERE u.username = $1
        GROUP BY u.username, r.display_value, l.display_value, u.inactive_dt
    """
    
    try:
        async with db_pool.acquire() as connection:
            usuarios = await connection.fetch(sql_query, search_term)
            log.info(f"Vista previa: Se encontró coincidencia para '{search_term}'")
            return [dict(u) for u in usuarios]
            
    except Exception as e:
        log.error(f"Error en vista previa para '{search_term}': {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail={"mensaje": "Error interno al buscar el usuario."}
        )

# USUARIO CONSULTA
@router.get("/consultar-usuario")
async def consultar_usuario_especifico(
    request: Request, 
    username: str = Query(..., title="username")
):
    db_pool = get_db_pool(request)
    
    if username.strip() == "":
        raise HTTPException(status_code=400, detail={"mensaje": "Debe proporcionar un nombre de usuario válido"})
    
    search_term = username.strip()
    log.info(f"CONSULTA: Buscando información detallada del usuario '{search_term}'")
    
    sql_query = """
        SELECT
        u.username AS "usuario",
        r.display_value AS "region",
        l.display_value AS "localidad",
        CASE 
            WHEN u.inactive_dt IS NULL THEN 'Activo' 
            ELSE 'Inactivo' 
        END AS "estado",
        COALESCE(STRING_AGG(rol_t.rol_name, ', '), 'Sin roles asignados') AS "roles_asignados",
        u.inactive_dt,
        u.origin_type,
        u.user_type,
        u.id_channel
    FROM SCC_USER.users u
    LEFT JOIN SCC_USER.region r ON u.id_region = r.id_region
    LEFT JOIN SCC_USER.location l ON u.id_location = l.id_location
    LEFT JOIN SCC_USER.user_rol ur ON u.username = ur.username
    LEFT JOIN SCC_USER.rol rol_t ON ur.id_rol = rol_t.id_rol
    WHERE u.username = $1
    GROUP BY u.username, r.display_value, l.display_value, u.inactive_dt, u.origin_type, u.user_type, u.id_channel
    """
    
    try:
        async with db_pool.acquire() as connection:
            usuarios = await connection.fetch(sql_query, search_term)
            log.info(f"Consulta finalizada. Usuario '{search_term}' {'encontrado' if usuarios else 'no existe'}.")
            return [dict(u) for u in usuarios]
            
    except Exception as e:
        log.error(f"Error consultando usuario específico '{search_term}': {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail={"mensaje": "Error interno al consultar el usuario."}
        )

# MAESTROS: LOCALIDADES POR REGIÓN (DUPLICADO EN TU CÓDIGO, SE MANTIENE POR CONSISTENCIA)
@router.get("/maestros/localidades")
async def obtener_localidades_maestro(
    request: Request, 
    region_id: int = Query(..., description="ID de la región")
):
    db_pool = get_db_pool(request)
    sql_query = "SELECT id_location, display_value FROM location WHERE id_region = $1 ORDER BY display_value;"
    try:
        async with db_pool.acquire() as connection:
            localidades = await connection.fetch(sql_query, region_id)
            return [dict(l) for l in localidades]
    except Exception as e:
        log.error(f"Error en catálogo de localidades: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"mensaje": "Error al consultar localidades."})

# MAESTROS: REGIONES
@router.get("/maestros/regiones")
async def obtener_regiones(request: Request):
    db_pool = get_db_pool(request)
    sql_query = "SELECT id_region, display_value FROM region ORDER BY display_value;"
    try:
        async with db_pool.acquire() as connection:
            regiones = await connection.fetch(sql_query)
            return [dict(r) for r in regiones]
    except Exception as e:
        log.error(f"Error en catálogo de regiones: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"mensaje": "Error al consultar regiones."})

# MAESTROS: ROLES
@router.get("/maestros/roles")
async def obtener_roles(request: Request):
    db_pool = get_db_pool(request)
    sql_query = "SELECT id_rol, rol_name FROM rol ORDER BY rol_name;"
    try:
        async with db_pool.acquire() as connection:
            roles = await connection.fetch(sql_query)
            return [dict(r) for r in roles]
    except Exception as e:
        log.error(f"Error en catálogo de roles: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"mensaje": "Error al consultar roles."})

# CONSULTAR USUARIO POR USERNAME
@router.get("/usuarios/{username}")
async def obtener_usuario_por_username(username: str, request: Request):
    db_pool = get_db_pool(request)
    log.debug(f"Buscando datos completos para edición del usuario: {username}")
    sql_query = """
        SELECT
            u.username, u.id_region, u.id_location, u.inactive_dt IS NULL AS is_active,
            STRING_AGG(ur.id_rol, ',') AS roles_ids, r.display_value AS region_name,
            l.display_value AS location_name, u.origin_type, u.user_type, u.id_channel
        FROM SCC_USER.users u
        LEFT JOIN SCC_USER.user_rol ur ON u.username = ur.username
        LEFT JOIN SCC_USER.region r ON u.id_region = r.id_region
        LEFT JOIN SCC_USER.location l ON u.id_location = l.id_location
        WHERE u.username = $1
        GROUP BY u.username, u.id_region, u.id_location, u.inactive_dt, r.display_value, l.display_value, u.origin_type, u.user_type, u.id_channel;
    """
    try:
        async with db_pool.acquire() as connection:
            usuario = await connection.fetchrow(sql_query, username)
            if not usuario:
                log.warning(f"Intento de consulta de usuario inexistente: {username}")
                raise HTTPException(status_code=404, detail="Usuario no encontrado.")
            return dict(usuario)
    except HTTPException: raise
    except Exception as e:
        log.error(f"Error al obtener usuario {username}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"mensaje": "Error interno"})

# ACTUALIZAR USUARIO
@router.put("/usuarios/{username}")
async def actualizar_usuario(username: str, data: ActualizarUsuario, request: Request):
    db_pool = get_db_pool(request)
    log.info(f"ACTUALIZACIÓN: Usuario '{username}' modificado por '{data.changedBy}'")
    
    sql_query = "SELECT scc_user.sp_actualizar_usuario($1, $2, $3, $4, $5, $6, $7, $8);"
    
    params = (
        username, data.id_region, data.location_name, data.id_rol,
        data.is_active, data.changedBy, data.user_type, data.id_channel   
    )
    
    log.debug(f"Parámetros SP actualizar_usuario: {params}")
    
    try:
        async with db_pool.acquire() as connection:
            resultado_db = await connection.fetchval(sql_query, *params)
            
        if resultado_db.startswith("EXITO"):
            log.info(f"ACTUALIZACIÓN EXITOSA: Usuario '{username}' actualizado correctamente.")
            return {"status": "EXITO", "mensaje": resultado_db}
        
        log.warning(f"ACTUALIZACIÓN RECHAZADA: La DB devolvió: {resultado_db} para {username}")
        raise HTTPException(status_code=400, detail={"estado": "ERROR", "mensaje": resultado_db})
    except HTTPException: raise
    except Exception as e:
        log.error(f"FALLO CRÍTICO en actualización de {username}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"mensaje": f"Fallo en la actualización: {e}"})