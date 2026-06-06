from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from .database import create_db_pool, close_db_pool
from .router import router

# --- 1. IMPORTACIÓN DEL CONTEXTO Y LOGGER ---
from api_gateway.utils.logger_config import user_context, setup_logger

# Inicializamos el logger para el servicio de Roles y Permisos
log = setup_logger("ROL-SERVICE")

app = FastAPI(title="Rol and Permissions Service")

# --- 2. MIDDLEWARE PARA CAPTURAR LA IDENTIDAD (X-User-ID) ---
@app.middleware("http")
async def set_logging_context(request: Request, call_next):
    # Leemos el header inyectado por el Gateway
    user_id = request.headers.get("X-User-ID") or \
              request.query_params.get("username") or \
              "SYSTEM"
    
    # Seteamos el contexto (máximo 12 caracteres para mantener la alineación)
    token = user_context.set(str(user_id)[:12])
    
    try:
        response = await call_next(request)
        return response
    finally:
        # Limpiamos el contexto al finalizar la petición
        user_context.reset(token)

# --- CONFIGURACIÓN DE CORS ---
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GESTIÓN DEL CICLO DE VIDA (Cambiados prints por log.info) ---
@app.on_event("startup")
async def startup():
    log.info("SISTEMA: Rol Service: Iniciando pool de conexiones...")
    await create_db_pool(app)

@app.on_event("shutdown")
async def shutdown():
    log.info("SISTEMA: Rol Service: Cerrando pool...")
    await close_db_pool(app)

# Prefijo /api/v1/roles para diferenciarlo de otros servicios
app.include_router(router, prefix="/api/v1/roles", tags=["Permisos"])