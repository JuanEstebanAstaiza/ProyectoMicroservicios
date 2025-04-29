from fastapi import FastAPI
from contextlib import asynccontextmanager

from microservice_metrics.app.api import metrics # Importar el router
from microservice_metrics.app.db.database import connect_to_redis, close_redis_connection # Importar funciones de conexión Redis

# --- Lifespan para gestionar la conexión a Redis ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código al inicio
    print("Ejecutando evento startup (Metrics)...")
    await connect_to_redis()
    print("Conexión a Redis establecida.")
    yield
    # Código al final
    print("Ejecutando evento shutdown (Metrics)...")
    await close_redis_connection()
    print("Conexión a Redis cerrada.")


# --- Instancia de la Aplicación FastAPI ---
app = FastAPI(
    title="Microservicio de Métricas",
    description="API para gestionar métricas simples (contadores) usando Redis.",
    version="1.0.0",
    lifespan=lifespan
)

# --- Incluir Routers ---
app.include_router(metrics.router)

# --- Ruta Raíz (Opcional) ---
@app.get("/", tags=["Root"])
async def read_root():
    """Ruta raíz simple para verificar que el servicio está funcionando."""
    return {"message": "Bienvenido al Microservicio de Métricas"}

# --- Punto de entrada para Uvicorn ---
if __name__ == "__main__":
    import uvicorn
    # Usar un puerto diferente a los otros servicios (ej. 8002)
    uvicorn.run(app, host="0.0.0.0", port=8002)