from fastapi import FastAPI
from contextlib import asynccontextmanager

from microservice_content.app.api import content # Importar el router
from microservice_content.app.db.database import init_db # Importar la función de inicialización de Beanie

# --- Lifespan para inicializar Beanie ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código a ejecutar ANTES de que la aplicación empiece
    print("Ejecutando evento startup...")
    await init_db() # Llama a la inicialización de Beanie/Motor
    print("Base de datos y Beanie inicializados.")
    yield
    # Código a ejecutar DESPUÉS de que la aplicación termine (si necesitas limpieza)
    print("Ejecutando evento shutdown...")
    # Motor/Beanie generalmente no requieren cierre explícito del cliente aquí
    # a menos que tengas lógica específica de limpieza.

# --- Instancia de la Aplicación FastAPI ---
app = FastAPI(
    title="Microservicio de Contenido (Async con Beanie)",
    description="API para gestionar contenido usando MongoDB con Beanie ODM.",
    version="1.1.0", # Incrementar versión
    lifespan=lifespan # Usar el lifespan para la inicialización
)

# --- Incluir Routers ---
app.include_router(content.router)

# --- Ruta Raíz (Opcional) ---
@app.get("/", tags=["Root"])
async def read_root():
    """Ruta raíz simple para verificar que el servicio está funcionando."""
    return {"message": "Bienvenido al Microservicio de Contenido (Async/Beanie)"}

# --- Punto de entrada para Uvicorn ---
if __name__ == "__main__":
    import uvicorn
    # uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
    uvicorn.run(app, host="0.0.0.0", port=8020)