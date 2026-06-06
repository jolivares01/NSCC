from fastapi import FastAPI, Request
from .router import router as report_router
from .database import create_db_pool

# --- 1. IMPORTACIÓN DEL CONTEXTO Y LOGGER ---
from api_gateway.utils.logger_config import user_context, setup_logger

# Inicializamos el logger para el servicio de Reportes
log = setup_logger("REPORT-SERVICE")

app = FastAPI(title="SCC Report Service")

# --- 2. MIDDLEWARE PARA CAPTURAR LA IDENTIDAD (X-User-ID) ---
@app.middleware("http")
async def set_logging_context(request: Request, call_next):
    # Leemos el header que inyectó el Gateway
    user_id = request.headers.get("X-User-ID") or \
              request.query_params.get("username") or \
              "SYSTEM"
    
    # Guardamos en la memoria volátil de esta petición (máx 12 caracteres)
    token = user_context.set(str(user_id)[:12])
    
    try:
        response = await call_next(request)
        return response
    finally:
        # Limpiamos el contexto al finalizar la respuesta
        user_context.reset(token)

@app.on_event("startup")
async def startup():
    log.info("SISTEMA: Iniciando Report Service...")
    app.state.db_pool = await create_db_pool()

# --- 3. MONTAJE DE RUTAS ---
app.include_router(report_router, prefix="/api/v1/reports")