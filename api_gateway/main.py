import os
import sys

# Agregamos la raíz del proyecto al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

# Importación de servicios
from scc_services.user_service.app.router import router as user_router
# Importación del router del dashboard
from scc_services.dashboard_service.app.router import router as dashboard_router
from scc_services.auth_service.app.router import router as auth_router
# gestion de reclamos
from scc_services.claims_service.app.router import router as claims_router
# gestion de roles
from scc_services.rol_services.app.router import router as rol_router

# Importamos la lógica de base de datos (usamos la de un servicio central o el de user_service como base)
from scc_services.user_service.app.database import create_db_pool, close_db_pool

app = FastAPI(title="API Gateway SCC")

# --- CONFIGURACIÓN DE CORS ---
origins = [
    "http://localhost:8080",
    "http://localhost:5173",
    "http://127.0.0.1:8080",
    "*" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GESTIÓN DEL CICLO DE VIDA ---
@app.on_event("startup")
async def startup():
    print("Iniciando API Gateway...")
    await create_db_pool(app)
    print("Pool de conexiones a PostgreSQL listo para todos los servicios.")

@app.on_event("shutdown")
async def shutdown():
    print("Apagando API Gateway...")
    await close_db_pool(app)

# --- MONTAJE DE RUTAS (ENDPOINTS) ---

# Rutas de Gestión de Usuarios
app.include_router(user_router, prefix="/api/v1/users", tags=["Gestión de Usuarios"])
# Rutas de Dashboard (Estadísticas de Ventas/Postventas)
app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["Dashboard"])
# Rutas de Autenticación
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Autenticación"])
# Rutas de Gestión de Reclamos
app.include_router(claims_router, prefix="/api/v1/claims", tags=["Gestión de Reclamos"])
# Rutas de Gestión de Roles
app.include_router(rol_router, prefix="/api/v1/roles", tags=["Gestión de Roles"])

@app.get("/")
async def root():
    return {"message": "SCC API Gateway operativo", "status": "healthy"}