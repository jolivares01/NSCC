# --- ETAPA 1: COMPILACIÓN DEL FRONTEND ---
FROM node:16-alpine AS front-build
WORKDIR /app/front
COPY scc_front/package*.json ./
RUN npm install
COPY scc_front/ .
RUN npm run build

# --- ETAPA 2: AMBIENTE UNIFICADO DE PRODUCCIÓN ---
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias esenciales del sistema, Nginx y Supervisor
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    supervisor \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar y servir los archivos estáticos del Front en Nginx
COPY --from=front-build /app/front/dist /usr/share/nginx/html

# Copiar e instalar requerimientos de Python (Gateway y Backend)
# Ajusta las rutas si manejas un solo requirements.txt o únelos en uno en la raíz
COPY api_gateway/requirements.txt ./requirements_gateway.txt
RUN pip install --no-cache-dir -r requirements_gateway.txt

# Copiar todo el código fuente del proyecto al contenedor
COPY . .

# Exponer el puerto 80 (Nginx servirá el Front y redirigirá al API)
EXPOSE 80
EXPOSE 8000
EXPOSE 8001

# Comando de arranque administrado por Supervisor
CMD ["/usr/bin/supervisord", "-c", "/app/supervisord.conf"]