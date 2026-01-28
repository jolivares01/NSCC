# scc_services/rol_services/app/main.py
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from .database import create_db_pool, close_db_pool
from .router import router

app = FastAPI(title="Rol and Permissions Service")

# CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    print("Rol Service: Iniciando pool de conexiones...")
    await create_db_pool(app)

@app.on_event("shutdown")
async def shutdown():
    print("Rol Service: Cerrando pool...")
    await close_db_pool(app)

# Prefijo /api/v1/roles para diferenciarlo de otros servicios
app.include_router(router, prefix="/api/v1/roles", tags=["Permisos"])