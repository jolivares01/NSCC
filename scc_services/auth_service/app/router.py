#'''
########### Para prueba en local
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timedelta
import jwt  # Asegúrate de tener instalado 'pyjwt'
from passlib.hash import bcrypt 
from .models import LoginRequest
from .database import get_db_pool
from .core.config import settings
router = APIRouter()

def create_access_token(data: dict):
    to_encode = data.copy()
    
    # 1. Usamos la expiración desde settings (centralizado)
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # 2. Usamos la SECRET_KEY y el ALGORITHM del objeto settings
    return jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )

@router.post("/login")
async def login_endpoint(data: LoginRequest, request: Request):
    db_pool = get_db_pool(request)
    
    try:
        async with db_pool.acquire() as connection:
            # PASO 1: Validar credenciales en la tabla temporal
            auth_query = """
                SELECT password_hash, id_rol 
                FROM scc_user.auth_temporal 
                WHERE username = $1 AND is_active = TRUE
            """
            auth_user = await connection.fetchrow(auth_query, data.username)
            
            if not auth_user:
                raise HTTPException(status_code=401, detail="Usuario no encontrado o inactivo")

            if not bcrypt.verify(data.password, auth_user['password_hash']):
                raise HTTPException(status_code=401, detail="Contraseña incorrecta")

            # PASO 2: Validar estado en la tabla users
            user_query = """
                SELECT username, origin_type
                FROM scc_user.users 
                WHERE username = $1 AND inactive_dt IS NULL
            """
            active_user = await connection.fetchrow(user_query, data.username)

            if not active_user:
                raise HTTPException(status_code=403, detail="Usuario inactivo en el sistema principal")

            # --- PASO 3: GENERACIÓN DEL TOKEN JWT ---
            token_data = {
                "sub": active_user["username"],
                "role": auth_user["id_rol"],
                "origin": active_user.get("origin_type", "LOCAL")
            }
            
            access_token = create_access_token(token_data)

            return {
                "estado": "EXITO",
                "access_token": access_token,
                "token_type": "bearer",
                "username": active_user['username'],
                "id_rol": auth_user['id_rol']
            }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en el proceso de autenticación local: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

'''
### TOKEN PRODUCCIÓN
from fastapi import APIRouter, HTTPException, Request
from ldap3 import Server, Connection, ALL, SIMPLE
import jwt
from datetime import datetime, timedelta
from .models import LoginRequest
from .database import get_db_pool
# --- IMPORTACIÓN CENTRALIZADA ---
from .core.config import settings 

router = APIRouter()

# --- FUNCIONES DE APOYO REFACTORIZADAS ---

def create_access_token(data: dict):
    """ Genera el token firmado usando la configuración del .env """
    to_encode = data.copy()
    # Usamos settings.ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # Usamos settings.SECRET_KEY y settings.ALGORITHM
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_user_and_role(connection, username_upper: str):
    """ Busca usuario activo y su rol en la BD """
    sql = """
        SELECT 
            u.username,
            UPPER(u.origin_type) AS origin_type,
            ur.id_rol
        FROM scc_user.users u
        INNER JOIN scc_user.user_rol ur ON u.username = ur.username
        WHERE u.username = $1 AND u.inactive_dt IS NULL
    """
    return await connection.fetchrow(sql, username_upper)

async def get_ldap_config_for_origin(connection, origin_type: str):
    """ Obtiene la configuración del servidor LDAP (Interno/Externo) de la BD """
    sql = """
        SELECT name AS ldap_name, server AS ldap_server, 
                port AS ldap_port, domain AS ldap_domain
        FROM scc_user.ldap_conf
        WHERE inactive_dt IS NULL AND UPPER(name) = UPPER($1)
        LIMIT 1
    """
    return await connection.fetchrow(sql, origin_type)

def infer_use_ssl(port) -> bool:
    """ Determina si usa SSL basado en el puerto (636 es LDAPS) """
    try:
        return int(port) == 636
    except Exception:
        return False

async def authenticate_ldap_with_config(*, username: str, password: str, server: str, port: int, domain: str) -> bool:
    """ Realiza el bind contra el servidor LDAP corporativo """
    use_ssl = infer_use_ssl(port)
    try:
        ldap_server = Server(server, port=int(port), use_ssl=use_ssl, get_info=ALL)
        user_upn = f"{username}@{domain}"
        # Conexión con timeout para evitar bloqueos en la red de Digitel
        conn = Connection(ldap_server, user=user_upn, password=password, 
                          authentication=SIMPLE, receive_timeout=6)
        if conn.bind():
            conn.unbind()
            return True
        return False
    except Exception as e:
        # Aquí podrías usar tu logger_config en lugar de print
        print(f"Error LDAP: {e}")
        return False

# --- ENDPOINT DE LOGIN ---

@router.post("/login")
async def login_endpoint(data: LoginRequest, request: Request):
    db_pool = get_db_pool(request)
    # Importante: el username debe coincidir con como esté en tu BD (usualmente UPPER)
    username_upper = data.username.upper() 

    async with db_pool.acquire() as connection:
        # 1. Validación de existencia y rol en base de datos
        user_row = await get_user_and_role(connection, username_upper)
        if not user_row:
            raise HTTPException(status_code=403, detail="Usuario sin permisos o inactivo")

        origin_type = user_row["origin_type"]
        
        # 2. Configuración LDAP según el origen del usuario
        ldap_conf = await get_ldap_config_for_origin(connection, origin_type)
        if not ldap_conf:
            raise HTTPException(status_code=503, detail=f"LDAP no configurado para {origin_type}")

        # 3. Autenticación física contra el servidor LDAP
        ok = await authenticate_ldap_with_config(
            username=username_upper,
            password=data.password,
            server=ldap_conf["ldap_server"],
            port=ldap_conf["ldap_port"],
            domain=ldap_conf["ldap_domain"],
        )

        if not ok:
            raise HTTPException(status_code=401, detail="Credenciales corporativas inválidas")

        # 4. GENERACIÓN DEL TOKEN JWT USANDO CONFIGURACIÓN CENTRALIZADA
        token_data = {
            "sub": user_row["username"],
            "role": user_row["id_rol"],
            "origin": origin_type
        }
        
        access_token = create_access_token(token_data)

        return {
            "estado": "EXITO",
            "access_token": access_token,
            "token_type": "bearer",
            "username": user_row["username"],
            "id_rol": user_row["id_rol"],
            "origin_type": origin_type
        }
##'''