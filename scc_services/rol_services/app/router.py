from fastapi import APIRouter, HTTPException, Request
from .models import UserPermissions
from .database import get_db_pool

router = APIRouter()

@router.get("/permissions/{id_rol}", response_model=UserPermissions)
async def get_permissions_by_role(id_rol: str, request: Request):
    db_pool = get_db_pool(request)
    
    try:
        async with db_pool.acquire() as connection:
            # JOIN entre módulos y permisos para obtener los strings de los paths
            query = """
                SELECT m.path 
                FROM scc_user.modules m
                JOIN scc_user.role_permissions rp ON m.id_module = rp.id_module
                WHERE rp.id_rol = $1 AND m.is_active = TRUE
            """
            rows = await connection.fetch(query, id_rol)
            
            # Si no hay filas, el rol no tiene permisos o no existe
            allowed_paths = [row['path'] for row in rows]
            
            return {
                "id_rol": id_rol,
                "paths": allowed_paths
            }

    except Exception as e:
        print(f"Error al consultar permisos: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener permisos del rol")