# Dockerfile para microservice-metrics (FastAPI + Redis Async)

# Usando la estructura Opción D para consistencia con la petición anterior
# (Aunque para este servicio simple, la estructura estándar sería más sencilla)

# Etapa 1: Base con Python
FROM python:3.10-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /ProyectoMicroservicios

# Etapa 2: Instalación de dependencias Python
FROM base AS python-deps

COPY requirements.txt /ProyectoMicroservicios/microservice_metrics/requirements.txt
WORKDIR /ProyectoMicroservicios/microservice_metrics

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Etapa 3: Aplicación final
FROM python-deps AS runtime

COPY ./app /ProyectoMicroservicios/microservice_metrics/app

ENV PYTHONPATH="/ProyectoMicroservicios"

WORKDIR /ProyectoMicroservicios

# Exponer el puerto para este servicio (diferente a los otros)
EXPOSE 8002

# Comando ajustado para apuntar al módulo correcto
CMD ["uvicorn", "microservice_metrics.app.main:app", "--host", "0.0.0.0", "--port", "8002"]