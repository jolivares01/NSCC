from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from .database import create_db_pool, close_db_pool
from .router import router

# --- 1. IMPORTACIÓN DEL CONTEXTO Y LOGGER ---
from api_gateway.utils.logger_config import user_context, setup_logger

# Inicializamos el logger para el servicio de Reclamos
log = setup_logger("CLAIMS-SERVICE")

app = FastAPI(title="Claims Service")

# --- 2. MIDDLEWARE PARA CAPTURAR LA IDENTIDAD (X-User-ID) ---
@app.middleware("http")
async def set_logging_context(request: Request, call_next):
    # Capturamos el usuario enviado por el Gateway en el Header
    user_id = request.headers.get("X-User-ID") or \
              request.query_params.get("username") or \
              "SYSTEM"
    
    # Seteamos el contexto para los logs de esta petición específica
    token = user_context.set(str(user_id)[:12])
    
    try:
        response = await call_next(request)
        return response
    finally:
        # Limpiamos el contexto al finalizar el ciclo de vida de la petición
        user_context.reset(token)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. GESTIÓN DEL CICLO DE VIDA (Cambiados prints por log.info) ---
@app.on_event("startup")
async def startup():
    log.info("SISTEMA: Claims Service: Iniciando pool de conexiones...")
    await create_db_pool(app)

@app.on_event("shutdown")
async def shutdown():
    log.info("SISTEMA: Claims Service: Cerrando pool...")
    await close_db_pool(app)

# Prefijo /api/claims para diferenciarlo del Auth Service
app.include_router(router, prefix="/api/claims", tags=["Gestión de Reclamos"])