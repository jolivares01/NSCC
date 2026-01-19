from fastapi import APIRouter, HTTPException, Query, Request
from .models import RegistroUsuario, ActualizarUsuario
from .database import get_db_pool

router = APIRouter()

# REGISTRO DE USUARIO
@router.post("/registrar-usuario")
async def registrar_usuario_endpoint(data: RegistroUsuario, request: Request):
    db_pool = get_db_pool(request)
    sql_query = "SELECT scc_user.sp_registrar_usuario($1, $2, $3, $4, $5);"
    params = (data.region, data.localidad, data.username, data.rol, data.createdBy)

    try:
        async with db_pool.acquire() as connection:
            resultado_db = await connection.fetchval(sql_query, *params)
    except Exception as e:
        print(f"Error técnico: {e}")
        raise HTTPException(status_code=500, detail={"mensaje": "Error de conexión con la DB"})

    # Si el SP devuelve algo que no empieza con EXITO, mandamos un 400 con ese mensaje
    if not resultado_db.startswith("EXITO"):
        raise HTTPException(status_code=400, detail={"estado": "ERROR", "mensaje": resultado_db})
    
    return {"estado": "EXITO", "mensaje": resultado_db}

# VISTA PREVIA DE USUARIOS
@router.get("/usuarios-vista-previa")
async def obtener_usuarios_vista_previa(request: Request, search: str = ""):
    db_pool = get_db_pool(request)
    
    # 1. Validar que search no sea vacío
    if not search or search.strip() == "":
        raise HTTPException(
            status_code=400, 
            detail={"mensaje": "Debe proporcionar un usuario para buscar"}
        )
    
    search_term = search.strip()
    
    # 2. Usar la misma query exacta que en /usuarios/{username}
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
        WHERE u.username = $1  -- EXACTO, igual que en /usuarios/{username}
        GROUP BY u.username, r.display_value, l.display_value, u.inactive_dt
    """
    
    try:
        async with db_pool.acquire() as connection:
            usuarios = await connection.fetch(sql_query, search_term)
            
            # Retornar lista (puede estar vacía)
            return [dict(u) for u in usuarios]
            
    except Exception as e:
        print(f"Error al buscar usuario {search_term}: {e}")
        raise HTTPException(
            status_code=500, 
            detail={"mensaje": "Error interno al buscar el usuario."}
        )

# USUARIO CONSULTA
from fastapi import APIRouter, HTTPException, Request, Query

@router.get("/consultar-usuario")
async def consultar_usuario_especifico(
    request: Request, 
    username: str = Query(
        ...,  # Obligatorio
        title="username",
        description="Nombre de usuario a buscar (búsqueda exacta)",
        example="E24455123"
    )
):
    """
    Consulta un usuario específico por nombre exacto para mostrar en tabla
    
    - **username** (obligatorio): Nombre de usuario a buscar
    
    **Ejemplo:**
    - `/consultar-usuario?username=E24455123`
    
    **Respuesta:** Lista con el usuario encontrado o lista vacía si no existe
    """
    db_pool = get_db_pool(request)
    
    # Validar que no sea string vacío
    if username.strip() == "":
        raise HTTPException(
            status_code=400, 
            detail={"mensaje": "Debe proporcionar un nombre de usuario válido"}
        )
    
    search_term = username.strip()
    print(f" Consultando usuario específico: '{search_term}'")
    
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
        WHERE u.username = $1  -- Búsqueda EXACTA
        GROUP BY u.username, r.display_value, l.display_value, u.inactive_dt
    """
    
    try:
        async with db_pool.acquire() as connection:
            usuarios = await connection.fetch(sql_query, search_term)
            
            # Log para depuración
            print(f" Usuarios encontrados: {len(usuarios)}")
            
            # Siempre retornar lista (puede estar vacía)
            return [dict(u) for u in usuarios]
            
    except Exception as e:
        print(f" Error consultando usuario '{search_term}': {e}")
        raise HTTPException(
            status_code=500, 
            detail={"mensaje": "Error interno al consultar el usuario."}
        )

# MAESTROS: LOCALIDADES POR REGIÓN
@router.get("/maestros/localidades")
async def obtener_localidades_por_region(
    request: Request, 
    region_id: int = Query(..., description="ID de la región")
):
    db_pool = get_db_pool(request)
    sql_query = """
        SELECT id_location, display_value 
        FROM location 
        WHERE id_region = $1 
        ORDER BY display_value;
    """
    try:
        async with db_pool.acquire() as connection:
            localidades = await connection.fetch(sql_query, region_id)
            return [dict(l) for l in localidades]
    except Exception as e:
        print(f"Error al obtener localidades: {e}")
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
        print(f"Error al obtener regiones: {e}")
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
        print(f"Error al obtener roles: {e}")
        raise HTTPException(status_code=500, detail={"mensaje": "Error al consultar roles."})

# CONSULTAR USUARIO
@router.get("/usuarios/{username}")
async def obtener_usuario_por_username(username: str, request: Request):
    db_pool = get_db_pool(request)
    sql_query = """
        SELECT
            u.username,
            u.id_region,
            u.id_location,
            u.inactive_dt IS NULL AS is_active,
            STRING_AGG(ur.id_rol, ',') AS roles_ids,
            r.display_value AS region_name,
            l.display_value AS location_name
        FROM SCC_USER.users u
        LEFT JOIN SCC_USER.user_rol ur ON u.username = ur.username
        LEFT JOIN SCC_USER.region r ON u.id_region = r.id_region
        LEFT JOIN SCC_USER.location l ON u.id_location = l.id_location
        WHERE u.username = $1
        GROUP BY u.username, u.id_region, u.id_location, u.inactive_dt, r.display_value, l.display_value;
    """
    try:
        async with db_pool.acquire() as connection:
            usuario = await connection.fetchrow(sql_query, username)
            if not usuario:
                raise HTTPException(status_code=404, detail="Usuario no encontrado.")
            return dict(usuario)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al obtener usuario {username}: {e}")
        raise HTTPException(status_code=500, detail={"mensaje": "Error interno al consultar el usuario."})

# ACTUALIZAR USUARIO
@router.put("/usuarios/{username}")
async def actualizar_usuario(username: str, data: ActualizarUsuario, request: Request):
    db_pool = get_db_pool(request)
    sql_query = "SELECT sp_actualizar_usuario($1, $2, $3, $4, $5, $6);"
    params = (
        username,
        data.id_region,
        data.location_name,
        data.id_rol,
        data.is_active,
        data.changedBy
    )
    try:
        async with db_pool.acquire() as connection:
            resultado_db = await connection.fetchval(sql_query, *params)
        if resultado_db.startswith("EXITO"):
            return {"status": "EXITO", "mensaje": resultado_db}
        raise HTTPException(status_code=400, detail={"estado": "ERROR", "mensaje": resultado_db})
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al actualizar usuario {username}: {e}")
        raise HTTPException(status_code=500, detail={"mensaje": f"Fallo en la actualización: {e}"})