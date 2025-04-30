# Dockerfile para microservice-users (Opción D - Usando nombre ProyectoMicroservicios)

# Etapa 1: Base con Python
FROM python:3.10-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo raíz simulando la raíz del proyecto real
WORKDIR /ProyectoMicroservicios

# Etapa 2: Instalación de dependencias Python
FROM base AS python-deps

# Copiar requirements.txt a la ubicación simulada del microservicio
COPY requirements.txt /ProyectoMicroservicios/microservice_users/requirements.txt

# Establecer WORKDIR temporalmente en la carpeta del microservicio
WORKDIR /ProyectoMicroservicios/microservice_users

# Instalar dependencias
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Etapa 3: Aplicación final
FROM python-deps AS runtime

# Copiar el código de la aplicación a la ubicación simulada
COPY ./app /ProyectoMicroservicios/microservice_users/app

# Establecer la variable PYTHONPATH para que Python busque desde /ProyectoMicroservicios
ENV PYTHONPATH="/ProyectoMicroservicios"

# Establecer el directorio de trabajo final
WORKDIR /ProyectoMicroservicios

# Exponer el puerto
EXPOSE 8000

# Comando para ejecutar la aplicación, apuntando al módulo dentro de la estructura simulada
CMD ["uvicorn", "microservice_users.app.main:app", "--host", "0.0.0.0", "--port", "8000"]