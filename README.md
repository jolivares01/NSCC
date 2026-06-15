# inicializar front
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
npm run serve
# inicializar BackEnd
desde la ruta: C:\Users\E24455144\OneDrive - CORPORACION DIGITEL, C.A\Documents\Desarrollos Soporte CRM\NSCC-main\NSCC-main
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\api_gateway\venv\Scripts\Activate.ps1
#.\venv\Scripts\Activate.ps1
python -m uvicorn api_gateway.main:app --reload --port 8000


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
├── scc_frontend/             
│   ├── src/
│   ├── public/
│   ├── Dockerfile            
│   └── package.json
│
├── api_gateway/              
│   ├── main.py
│   ├── Utils/
│   │       └── logger_config.py (archvio para configuración de logs por cada servicio)
│   └── Dockerfile
│
├── services/                 
│   ├── user_service/         
│   │   └── app/
│   │       ├── main.py
│   │       ├── database.py
│   │       ├── models.py
│   │       ├── router.py
│   │       └── Dockerfile
│   ├── claims_service/
│   ├── reports_service/
│   ├── auth_service/    
│   ├── bussiness_rule_service/
│   ├── calculation_service/
│   ├── dashboard_service/
│   └── rol_service/
│
│
├── k8s/                      
│   ├── frontend-deploy.yaml
│   ├── api_gateway-deploy.yaml
│   ├── service-deploy.yaml     (se colocará un yaml por servicio)
│   └── postgres-statefulset.yaml
│
└── docker-compose.yml        


# Comandos Docker

# 1. Compilar todo el ecosistema (Front, Gateway y los 8 servicios)
docker compose build

# 2. Levantar toda la suite en segundo plano inyectando el .env oficial
docker compose --env-file .env up -d

# 3. Monitorear que los 10 contenedores estén corriendo en producción
docker compose ps