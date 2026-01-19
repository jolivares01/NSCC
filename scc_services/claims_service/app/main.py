from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from .database import create_db_pool, close_db_pool
from .router import router

app = FastAPI(title="Claims Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    print("Claims Service: Iniciando pool de conexiones...")
    await create_db_pool(app)

@app.on_event("shutdown")
async def shutdown():
    print("Claims Service: Cerrando pool...")
    await close_db_pool(app)

# Prefijo /api/claims para diferenciarlo del Auth Service
app.include_router(router, prefix="/api/claims", tags=["Gestión de Reclamos"])