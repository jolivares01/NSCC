# scc_services/auth_service/app/main.py
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from .database import create_db_pool, close_db_pool
from .router import router

app = FastAPI(title="Auth Service")

# CORS
origins = ["*"] # En desarrollo puedes dejarlo así

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ciclo de vida del pool de conexiones
@app.on_event("startup")
async def startup():
    print("Auth Service: Iniciando pool de conexiones...")
    await create_db_pool(app)

@app.on_event("shutdown")
async def shutdown():
    print("Auth Service: Cerrando pool...")
    await close_db_pool(app)

# Montar router bajo el prefijo /api
app.include_router(router, prefix="/api", tags=["Autenticación"])