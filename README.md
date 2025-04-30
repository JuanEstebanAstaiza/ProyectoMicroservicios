# ProyectoMicroservicios 

## Descripción Breve

Este proyecto implementa un sistema backend basado en microservicios con persistencia políglota (PostgreSQL, MongoDB, Redis) para una plataforma simplificada de gestión de contenido. El backend está contenerizado con Docker, orquestado localmente con Docker Compose y preparado para despliegue en Kubernetes (Minikube / Docker Desktop). Incluye también un cliente de escritorio simple desarrollado con PyQt5 que interactúa con el backend exclusivamente a través de sus APIs REST.

## Arquitectura Backend

El backend sigue un patrón de microservicios, compuesto por tres servicios principales:

1.  **Microservicio de Usuarios (`microservice_users`)**:
    * **Responsabilidad:** Gestionar la información de los usuarios (creación, lectura, actualización, eliminación).
    * **Tecnología:** Python, FastAPI, SQLAlchemy (ORM).
    * **Base de Datos:** PostgreSQL (Relacional).
    * **Puerto:** 8000

2.  **Microservicio de Contenido (`microservice_content`)**:
    * **Responsabilidad:** Gestionar los ítems de contenido (artículos, notas, etc.) con una estructura flexible.
    * **Tecnología:** Python, FastAPI, Beanie ODM (Async).
    * **Base de Datos:** MongoDB (NoSQL - Documental).
    * **Puerto:** 8020

3.  **Microservicio de Métricas (`microservice_metrics`)**:
    * **Responsabilidad:** Gestionar contadores simples para métricas diversas (ej. visitas).
    * **Tecnología:** Python, FastAPI, redis-py (Async).
    * **Base de Datos:** Redis (NoSQL - Clave/Valor In-Memory).
    * **Puerto:** 8002

## Persistencia Políglota - Justificación

Este proyecto aplica el concepto de persistencia políglota, utilizando diferentes bases de datos según las necesidades de cada microservicio:

* **PostgreSQL (Microservicio de Usuarios):**  Se eligió una base de datos relacional (SQL) para los usuarios debido a la naturaleza estructurada de sus datos (ID, email, nombre, contraseña hasheada, estado). Las relaciones (aunque no implementadas en este ejemplo básico) y las garantías ACID son importantes para la gestión de identidades y la integridad de los datos de usuario. SQLAlchemy facilita el mapeo objeto-relacional.
* **MongoDB (Microservicio de Contenido):**  Se optó por una base de datos NoSQL documental (MongoDB) para el contenido, ya que permite una mayor flexibilidad en la estructura de los ítems (ej. campo `extra_data` de tipo diccionario libre ). Esto es ideal para contenido que puede evolucionar o tener campos variables. Beanie ODM sobre Motor permite trabajar con MongoDB de forma asíncrona y cómoda con modelos Pydantic.
* **Redis (Microservicio de Métricas):**  Para métricas simples como contadores, una base de datos NoSQL en memoria clave-valor como Redis es extremadamente eficiente. Ofrece operaciones atómicas de incremento (`INCRBY`)  muy rápidas, ideales para este tipo de caso de uso donde la velocidad de escritura es prioritaria sobre la complejidad de las consultas o la persistencia a largo plazo (aunque se configura persistencia básica).

## Cliente Desktop PyQt (`client_pyqt`)

Se incluye una aplicación de escritorio simple (`client_pyqt/main_window.py`) desarrollada con PyQt5.

* **Propósito:** Actúa como un dashboard de administración/visualización básico.
* **Interacción:** Se comunica con los microservicios backend **exclusivamente** a través de sus APIs REST, utilizando una clase `ApiClient` (`client_pyqt/api_client/client.py`) que encapsula las llamadas HTTP con la librería `requests`.
* **Funcionalidad:**
    * Visualiza listas de usuarios, contenido y métricas en tablas separadas por pestañas.
    * Permite simular el login como "viewer" o "admin" (ID=1).
    * Permite (como admin) crear y eliminar usuarios.
    * Permite (como admin) crear contenido (título, cuerpo, autor, tags).
    * Permite (como admin) incrementar la métrica `homepage_visits`.
    * Permite visualizar el cuerpo completo de un ítem de contenido haciendo doble clic en su fila en la tabla.

## Tecnologías Principales

* **Backend:** Python 3.10+, FastAPI
* **Bases de Datos:** PostgreSQL (con SQLAlchemy), MongoDB (con Beanie ODM y Motor), Redis (con redis-py async)
* **Frontend:** PyQt5
* **Contenerización:** Docker, Docker Compose
* **Orquestación:** Kubernetes (Manifiestos para Minikube/Docker Desktop K8s)
* **Comunicación Cliente-Servidor:** RESTful APIs, Requests (librería Python)


## Instrucciones de Configuración y Ejecución

### Prerrequisitos

* Git
* Docker y Docker Compose
* Python 3.10 o superior
* `kubectl` (Herramienta de línea de comandos de Kubernetes)
* Un clúster Kubernetes local (Minikube o Kubernetes habilitado en Docker Desktop)

### 1. Clonar Repositorio

git clone <URL_DEL_REPOSITORIO>
cd ProyectoMicroservicios


### 2. Configuración Inicial (Secrets)

* El archivo kubernetes/secrets.yaml define la contraseña para PostgreSQL.
* El valor por defecto es para la contraseña 'password'. Si usas otra contraseña, necesitas codificarla en Base64 y actualizar el archivo:

* echo -n 'password' | base64

* Pega el resultado en secrets.yaml reemplazando el valor de POSTGRES_PASSWORD.

### 3. Construir Imágenes Docker

Construye las imágenes para cada microservicio desde la raíz del proyecto:

* docker build -t users-service:latest ./microservice_users
* docker build -t content-service:latest ./microservice_content
* docker build -t metrics-service:latest ./microservice_metrics

### 4. Ejecutar con Docker Compose (Local)

Esta es la forma más sencilla de levantar el backend localmente.

* Iniciar servicios: Desde la raíz del proyecto (ProyectoMicroservicios/), ejecuta:
*docker-compose up -d*.
El -d ejecuta los contenedores en segundo plano. Espera a que todas las bases de datos y servicios inicien. La primera vez puede tardar un poco mientras se descargan imágenes y se inicializan las bases de datos.
* Ver logs:
* *docker-compose logs -f* # Muestra logs de todos los servicios en tiempo real
* *docker-compose logs users-service* # Muestra logs solo de un servicio
*  Detener servicios:
* *docker-compose down* # Detiene y elimina los contenedores

### 5. Desplegar en Kubernetes (Minikube / Docker Desktop)

#### 5.1. Preparar Kubernetes y Cargar Imágenes

* Asegúrate de que tu clúster Kubernetes local esté corriendo.
* Verifica que *kubectl* apunta al contexto correcto (*docker-desktop o minikube*):
* *kubectl config current-context*
* *Si usas Minikube*, carga las imágenes construidas localmente en el clúster:
* *minikube image load users-service:latest*
* *minikube image load content-service:latest*
* *minikube image load metrics-service:latest*

(Si usas Docker Desktop K8s, normalmente puede acceder a las imágenes locales directamente).

#### 5.2. Aplicar Manifiestos

* Aplica todos los archivos de configuración desde la raíz del proyecto:
* *kubectl apply -f kubernetes/*

#### 5.3. Verificar Estado

* Espera a que todos los Pods estén *Running (READY 1/1)*:
* *kubectl get pods -w*

* Verifica los Services y PVCs:
* *kubectl get svc*
* *kubectl get pvc*

* Revisa logs si algún Pod falla (especialmente el init container de content-deployment o los pods de bases de datos):
* *kubectl logs <nombre-del-pod>*

#### 5.4. Exponer Servicios para Cliente Local (Port-Forwarding)

* Para que el cliente PyQt (corriendo en tu host) pueda acceder a los servicios dentro de Kubernetes, necesitas abrir túneles *port-forward*. Abre terminales separadas para cada uno y mantenlos corriendo mientras usas el cliente:
* ##### Terminal 1
* *kubectl port-forward service/users-service 8000:8000*
* ##### Terminal 2
* *kubectl port-forward service/content-service 8020:8020*
* ##### Terminal 3
* *kubectl port-forward service/metrics-service 8002:8002*

#### 5.5. Eliminar Despliegue

 * *kubectl delete -f kubernetes/*
 * Opcional: Borrar PVCs y ConfigMap del script SQL
 * *kubectl delete pvc --all*
 * *kubectl delete configmap postgres-init-sql*

### 6. Ejecutar Cliente PyQt

 * Navega a la carpeta del cliente: cd client_pyqt
 * Instala las dependencias
   

