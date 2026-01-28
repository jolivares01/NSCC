# Inicializar Capa Front
npm run serve
# Inicializar Capa BackEnd 
1. python -m venv venv
2. .\venv\Scripts\Activate.ps1

para instalar fastAPI
1. pip install fastapi uvicorn asyncpg httpx pydantic[email]

Para ejecutar el gateway:
1. python -m uvicorn main:app --reload --port 8000 (Se debe ejecutar dentro de la ruta del API)

Validar Swagger de Api gestion de usuarios:
http://localhost:8000/docs#/

# Documentación de Arquitectura

SCC_PROJECT_ROOT/
├── scc_frontend/             # proyecto Vue actual
│   ├── src/
│   ├── public/
│   ├── Dockerfile            # Para servir con Nginx
│   └── package.json
│
├── api_gateway/              # El orquestador de tus servicios
│   ├── main.py
│   └── Dockerfile
│
├── services/                 # Agrupamos tus microservicios
│   ├── user_service/         
│   │   └── app/
│   │       ├── main.py
│   │       ├── database.py
│   │       ├── models.py│
│   │       ├── router.py
│   │       └── Dockerfile
│   ├── claims_service/
│   └── reports_service/
│
├── k8s/                      # Archivos de configuración de Kubernetes
│   ├── frontend-deploy.yaml
│   ├── service-deploy.yaml     (se colocará un yaml por servicio)
│   └── postgres-statefulset.yaml
│
└── docker-compose.yml        