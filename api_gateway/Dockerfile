FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependencias esenciales del sistema para psycopg2 / Postgres
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && apt-get clean && rm -rf /var/lib/apt/lists/*

# CORRECCIÓN AQUÍ: Copiamos el requirements.txt global de la raíz
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código específico de la API Gateway al entorno de ejecución
COPY api_gateway/ .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]