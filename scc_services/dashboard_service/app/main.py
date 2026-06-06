from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from .database import create_db_pool, close_db_pool
from .router import router

# --- 1. IMPORTACIÓN DEL CONTEXTO Y LOGGER ---
from api_gateway.utils.logger_config import user_context, setup_logger

# Inicializamos el logger para el servicio de Dashboard
log = setup_logger("DASHBOARD-SERVICE")

app = FastAPI(title="Dashboard Service")

# --- 2. MIDDLEWARE PARA CAPTURAR LA IDENTIDAD DESDE EL GATEWAY ---
@app.middleware("http")
async def set_logging_context(request: Request, call_next):
    # Leemos el Header 'X-User-ID' inyectado por el API Gateway
    user_id = request.headers.get("X-User-ID") or \
              request.query_params.get("username") or \
              "SYSTEM"
    
    # Seteamos el contexto para los logs de esta petición (máximo 12 caracteres)
    token = user_context.set(str(user_id)[:12])
    
    try:
        response = await call_next(request)
        return response
    finally:
        # Limpiamos el contexto al terminar la petición para evitar fugas de memoria
        user_context.reset(token)

# CORS (Mantenemos la configuración de seguridad que ya tienes)
origins = ["*"] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ciclo de vida del Pool de conexiones (Cambiados prints por log.info)
@app.on_event("startup")
async def startup():
    log.info("SISTEMA: Dashboard Service: Iniciando pool de conexiones...")
    await create_db_pool(app)

@app.on_event("shutdown")
async def shutdown():
    log.info("SISTEMA: Dashboard Service: Cerrando pool...")
    await close_db_pool(app)

# Montar las rutas del Dashboard
app.include_router(router, prefix="/api/dashboard", tags=["Dashboard"])