from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from .database import create_db_pool, close_db_pool
from .router import router

# --- 1. IMPORTACIÓN DEL CONTEXTO Y LOGGER ---
from api_gateway.utils.logger_config import user_context, setup_logger

# Inicializamos el logger para el servicio de Usuarios
log = setup_logger("USER-SERVICE")

app = FastAPI(title="User Service")

router.app = app

# --- 2. MIDDLEWARE PARA CAPTURAR LA IDENTIDAD DESDE EL GATEWAY ---
@app.middleware("http")
async def set_logging_context(request: Request, call_next):
    # Leemos el Header 'X-User-ID' inyectado por el API Gateway
    user_id = request.headers.get("X-User-ID") or \
              request.query_params.get("username") or \
              "SYSTEM"
    
    # Seteamos el contexto (máximo 12 caracteres)
    token = user_context.set(str(user_id)[:12])
    
    try:
        response = await call_next(request)
        return response
    finally:
        # Limpiamos el contexto al terminar la petición
        user_context.reset(token)

# CORS
origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "null",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ciclo de vida (Cambiados prints por log.info para consistencia)
@app.on_event("startup")
async def startup():
    log.info("SISTEMA: Iniciando pool de conexiones a la base de datos...")
    await create_db_pool(app)

@app.on_event("shutdown")
async def shutdown():
    log.info("SISTEMA: Cerrando pool de conexiones a la base de datos...")
    await close_db_pool(app)

# Montar router
app.include_router(router, prefix="/api", tags=["Usuarios"])