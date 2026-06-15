FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && apt-get clean && rm -rf /var/lib/apt/lists/*

# 1. Copia el requirements.txt desde la raíz global (Ya que el contexto ahora es .)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. MODIFICACIÓN AQUÍ: Cambia el COPY anterior por la ruta específica del servicio
# Por ejemplo, para el auth_service debe decir:
COPY scc_services/auth_service/ .

# (Para el user_service dirá: COPY scc_services/user_service/ ., etc.)

EXPOSE 8000

CMD ["python", "main.py"]