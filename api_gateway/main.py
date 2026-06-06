import os
import sys
import time 
import jwt  
from starlette.datastructures import MutableHeaders

# Agregamos la raíz del proyecto al path para encontrar los microservicios
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

# --- IMPORTACIÓN DE CONFIGURACIÓN, LOGGER Y CONTEXTO ---
from api_gateway.config import settings
from api_gateway.utils.logger_config import setup_logger, user_context

# Importación de servicios (Routers)
from scc_services.user_service.app.router import router as user_router
from scc_services.dashboard_service.app.router import router as dashboard_router
from scc_services.auth_service.app.router import router as auth_router
from scc_services.claims_service.app.router import router as claims_router
from scc_services.rol_services.app.router import router as rol_router
from scc_services.calculation_service.app.router import router as calculation_router
from scc_services.report_service.app.router import router as report_router
from scc_services.business_rules_service.app.router import router as business_rules_router

# Lógica de base de datos compartida (Desde el servicio de usuarios / esto para que el gateway pueda establecer una conexion de base de datos)
from scc_services.user_service.app.database import create_db_pool, close_db_pool

app = FastAPI(title="API Gateway SCC")

# Inicialización del logger principal del Gateway
log = setup_logger("API-GATEWAY")

# --- MIDDLEWARE DE LOGGING Y PROPAGACIÓN DE IDENTIDAD ---
@app.middleware("http")
async def log_operations(request: Request, call_next):
    """
    Middleware encargado de interceptar todas las peticiones, 
    extraer el usuario del token y propagarlo a los logs y microservicios.
    """
    user_id = "SYSTEM"
    
    # 1. Intentar obtener el usuario decodificando el JWT
    auth_header = request.headers.get("Authorization") or request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            token = auth_header.split(" ")[1]
            # Usamos la SECRET_KEY y ALGORITHM desde settings (2026)
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            user_id = payload.get("sub", "SYSTEM")
        except Exception:
            # Si el token es inválido o expiró, marcamos como INV_TOKEN para auditoría
            user_id = "INV_TOKEN"

    # 2. Respaldo por Query Params si el token no traía información (para debug o admins)
    if user_id in ["SYSTEM", "INV_TOKEN"]:
        user_id = request.query_params.get("username") or \
                  request.query_params.get("admin_user") or \
                  user_id
    
    # --- PASO CRÍTICO: PROPAGACIÓN DE CONTEXTO ---
    # Guardamos el usuario en ContextVar (para que setup_logger lo imprima en cada línea)
    token_context = user_context.set(str(user_id)[:10])
    
    # Inyectamos el usuario en los Headers para que los Microservicios lo hereden (X-User-ID)
    new_headers = MutableHeaders(request._headers)
    new_headers["X-User-ID"] = str(user_id)
    request._headers = new_headers
    
    log.debug(f"OPERACIÓN INICIADA: {request.method} {request.url.path}")
    
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000 
        
        log.info(
            f"OPERACIÓN COMPLETADA: {request.method} {request.url.path} "
            f"| STATUS: {response.status_code} | TIEMPO: {process_time:.2f}ms"
        )
        return response

    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        log.error(
            f"ERROR CRÍTICO: {request.method} {request.url.path} "
            f"| MENSAJE: {str(e)} | TIEMPO: {process_time:.2f}ms", 
            exc_info=True 
        )
        raise e
    finally:
        # Limpiamos el contexto al terminar la petición para evitar fugas de memoria
        user_context.reset(token_context)

# --- CONFIGURACIÓN DE CORS (Cross-Origin Resource Sharing) ---
origins = ["http://localhost:8080", "http://localhost:5173", "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"], 
)

# --- GESTIÓN DEL CICLO DE VIDA (LIFESPAN) ---
@app.on_event("startup")
async def startup():
    log.info("SISTEMA: Iniciando API Gateway...")
    try:
        await create_db_pool(app)
        log.info("SISTEMA: Pool de conexiones PostgreSQL establecido correctamente.")
    except Exception as e:
        log.error(f"SISTEMA: Error al establecer el pool de conexiones: {e}")

@app.on_event("shutdown")
async def shutdown():
    log.info("SISTEMA: Apagando API Gateway...")
    try:
        await close_db_pool(app)
        log.info("SISTEMA: Conexiones cerradas.")
    except Exception:
        # Silenciamos errores de cierre si el loop ya se canceló
        pass

# --- REGISTRO DE RUTAS DE MICROSERVICIOS ---
app.include_router(user_router, prefix="/api/v1/users", tags=["Gestión de Usuarios"])
app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Autenticación"])
app.include_router(claims_router, prefix="/api/v1/claims", tags=["Gestión de Reclamos"])
app.include_router(rol_router, prefix="/api/v1/roles", tags=["Gestión de Roles"])
app.include_router(calculation_router, prefix="/api/v1/calculation", tags=["Motor de Cálculo"])
app.include_router(report_router, prefix="/api/v1/reports", tags=["Servicio de Reportes"])
app.include_router(business_rules_router, prefix="/api/v1/business-rules", tags=["Reglas de Negocio"])

@app.get("/")
async def root():
    return {
        "message": "SCC API Gateway operativo", 
        "version": "2.0.0",
        "status": "healthy",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }