from fastapi import APIRouter, HTTPException, Request
from passlib.hash import bcrypt
from .models import LoginRequest
from .database import get_db_pool

router = APIRouter()

@router.post("/login")
async def login_endpoint(data: LoginRequest, request: Request):
    db_pool = get_db_pool(request)
    
    try:
        async with db_pool.acquire() as connection:
            # PASO 1: Validar credenciales en la tabla temporal
            # Solo buscamos la contraseña y el rol
            auth_query = """
                SELECT password_hash, id_rol 
                FROM scc_user.auth_temporal 
                WHERE username = $1 AND is_active = TRUE
            """
            auth_user = await connection.fetchrow(auth_query, data.username)
            
            if not auth_user:
                raise HTTPException(status_code=401, detail="Credenciales inválidas")

            # Verificar la contraseña antes de seguir
            if not bcrypt.verify(data.password, auth_user['password_hash']):
                raise HTTPException(status_code=401, detail="Contraseña incorrecta")

            # PASO 2: Validar estado en la tabla users
            # Verificamos que el usuario exista y que inactive_dt sea NULL
            user_query = """
                SELECT username 
                FROM scc_user.users 
                WHERE username = $1 AND inactive_dt IS NULL
            """
            active_user = await connection.fetchrow(user_query, data.username)

            if not active_user:
                raise HTTPException(
                    status_code=403, 
                    detail="Usuario inactivo o no autorizado"
                )

            # Si ambos pasos pasan, devolvemos el éxito
            return {
                "estado": "EXITO",
                "username": active_user['username'],
                "id_rol": auth_user['id_rol']
            }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en el proceso de autenticación: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")