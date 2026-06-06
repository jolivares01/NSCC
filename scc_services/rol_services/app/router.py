from fastapi import APIRouter, HTTPException, Request
from .models import UserPermissions
from .database import get_db_pool
# --- IMPORTACIÓN DEL CONFIGURADOR DE LOGS ---
from api_gateway.utils.logger_config import setup_logger

# Inicialización del logger
log = setup_logger("ROL-SERVICE")

router = APIRouter()

@router.get("/permissions/{id_rol}", response_model=UserPermissions)
async def get_permissions_by_role(id_rol: str, request: Request):
    db_pool = get_db_pool(request)
    
    # DEBUG: Para verificar qué rol está solicitando permisos al navegar
    log.debug(f"Solicitud de carga de permisos para el rol: {id_rol}")
    
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
            
            # Procesamos las filas obtenidas
            allowed_paths = [row['path'] for row in rows]
            
            # INFO: Verificamos si el rol tiene acceso a algo
            if not allowed_paths:
                log.warning(f"El rol {id_rol} consultado no tiene módulos activos asignados.")
            else:
                log.info(f"Permisos cargados para {id_rol}: {len(allowed_paths)} rutas autorizadas.")
            
            # DEBUG: Opcional para ver qué rutas exactamente se están enviando al Front
            log.debug(f"Paths autorizados para {id_rol}: {allowed_paths}")
            
            return {
                "id_rol": id_rol,
                "paths": allowed_paths
            }

    except Exception as e:
        # ERROR: Reemplazamos el print por un log estructurado con rastro de error
        log.error(f"Error crítico al consultar permisos para el rol {id_rol}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al obtener permisos del rol")