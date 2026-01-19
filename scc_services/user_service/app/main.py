from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from .database import create_db_pool, close_db_pool
from .router import router

app = FastAPI(title="User Service")

router.app = app

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

# Ciclo de vida
@app.on_event("startup")
async def startup():
    print("Iniciando pool de conexiones a la base de datos...")
    await create_db_pool(app)

@app.on_event("shutdown")
async def shutdown():
    print("Cerrando pool de conexiones a la base de datos...")
    await close_db_pool(app)

# Montar router
app.include_router(router, prefix="/api", tags=["Usuarios"])