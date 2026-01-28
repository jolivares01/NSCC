# Documentación de Arquitectura

SCC_PROJECT_ROOT/
├── scc_frontend/             # Tu proyecto Vue actual
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
│   ├── user_service/         # Lo que mostraste en la imagen
│   │   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   └── Dockerfile
│   ├── claims_service/
│   └── reports_service/
│
├── k8s/                      # Archivos de configuración de Kubernetes
│   ├── frontend-deploy.yaml
│   ├── user-service-deploy.yaml
│   └── postgres-statefulset.yaml
│
└── docker-compose.yml        # Para desarrollo local rápido