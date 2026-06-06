from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from .database import create_db_pool, close_db_pool
from .router import router as calculation_router

# --- 1. IMPORTACIÓN DEL CONTEXTO Y LOGGER ---
from api_gateway.utils.logger_config import user_context, setup_logger

# Inicializamos el logger para el servicio de Cálculo
log = setup_logger("CALCULATION-SERVICE")

app = FastAPI(title="Calculation Service")

# --- 2. MIDDLEWARE PARA CAPTURAR LA IDENTIDAD DESDE EL GATEWAY ---
@app.middleware("http")
async def set_logging_context(request: Request, call_next):
    # Leemos el Header 'X-User-ID' inyectado por el API Gateway
    user_id = request.headers.get("X-User-ID") or \
              request.query_params.get("username") or \
              "SYSTEM"
    
    # Seteamos el contexto para los logs de esta petición
    token = user_context.set(str(user_id)[:12])
    
    try:
        response = await call_next(request)
        return response
    finally:
        # Limpiamos el contexto al terminar
        user_context.reset(token)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    log.info("SISTEMA: Iniciando Calculation Service...")
    await create_db_pool(app)

@app.on_event("shutdown")
async def shutdown():
    log.info("SISTEMA: Apagando Calculation Service...")
    await close_db_pool(app)

# Montar las rutas del servicio de cálculo
app.include_router(calculation_router, prefix="/api/v1/calculation", tags=["Motor de Cálculo"])