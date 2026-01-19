from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from .database import create_db_pool, close_db_pool
from .router import router

app = FastAPI(title="Dashboard Service")

# CORS (Mantenemos la configuración de seguridad que ya tienes)
origins = ["*"] # Ajustar según necesidades de producción

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ciclo de vida del Pool de conexiones
@app.on_event("startup")
async def startup():
    print("Dashboard Service: Iniciando pool de conexiones...")
    await create_db_pool(app)

@app.on_event("shutdown")
async def shutdown():
    print("Dashboard Service: Cerrando pool...")
    await close_db_pool(app)

# Montar las rutas del Dashboard
app.include_router(router, prefix="/api/dashboard", tags=["Dashboard"])