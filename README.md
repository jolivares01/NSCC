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