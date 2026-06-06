from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from .database import create_db_pool, close_db_pool
from .router import router as business_rules_router

# --- IMPORTACIÓN DEL CONTEXTO DE LOGS ---
# Asegúrate de que la ruta de importación sea correcta según tu estructura
from api_gateway.utils.logger_config import user_context, setup_logger

# Inicializamos el logger para el servicio
log = setup_logger("BUSINESS-RULES")

app = FastAPI(
    title="Business Rules Service",
    description="Servicio para la gestión paramétrica de comisiones (Planes, Servicios y OT)",
    version="1.0.0"
)

# --- MIDDLEWARE PARA CAPTURAR EL USUARIO DEL GATEWAY ---
@app.middleware("http")
async def set_logging_context(request: Request, call_next):
    # 1. Leemos el "susurro" (Header) que inyectó el Gateway
    # Si no viene, buscamos en query params o ponemos SYSTEM
    user_id = request.headers.get("X-User-ID") or \
              request.query_params.get("username") or \
              "SYSTEM"
    
    # 2. Guardamos el usuario en la memoria de esta petición (ContextVar)
    token = user_context.set(str(user_id)[:12])
    
    try:
        response = await call_next(request)
        return response
    finally:
        # 3. Limpiamos al terminar la petición
        user_context.reset(token)

# --- CONFIGURACIÓN DE CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GESTIÓN DEL CICLO DE VIDA ---
@app.on_event("startup")
async def startup():
    log.info("SISTEMA: Iniciando Business Rules Service...") # Cambiado print por log
    await create_db_pool(app)

@app.on_event("shutdown")
async def shutdown():
    log.info("SISTEMA: Apagando Business Rules Service...") # Cambiado print por log
    await close_db_pool(app)

# --- MONTAJE DE RUTAS ---
app.include_router(
    business_rules_router, 
    prefix="/api/v1/business-rules", 
    tags=["Reglas de Negocio"]
)

@app.get("/")
async def root():
    return {"service": "Business Rules Service", "status": "online"}