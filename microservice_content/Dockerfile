# Dockerfile para microservice-content (Opción D - Usando nombre ProyectoMicroservicios)

# Etapa 1: Base con Python
FROM python:3.10-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /ProyectoMicroservicios

# Etapa 2: Instalación de dependencias Python
FROM base AS python-deps

COPY init_content_db.py /ProyectoMicroservicios/init_content_db.py
COPY requirements.txt /ProyectoMicroservicios/microservice_content/requirements.txt
WORKDIR /ProyectoMicroservicios/microservice_content

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Etapa 3: Aplicación final
FROM python-deps AS runtime

COPY ./app /ProyectoMicroservicios/microservice_content/app

ENV PYTHONPATH="/ProyectoMicroservicios"

WORKDIR /ProyectoMicroservicios

EXPOSE 8001

# Comando ajustado para apuntar al módulo dentro de la estructura simulada
CMD ["uvicorn", "microservice_content.app.main:app", "--host", "0.0.0.0", "--port", "8020"]