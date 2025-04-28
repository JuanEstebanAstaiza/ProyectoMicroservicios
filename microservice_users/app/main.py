from fastapi import FastAPI
from microservice_users.app.api import users # Importar el router de usuarios
from microservice_users.app.db import database # Importar para crear tablas
from microservice_users.app.schemas import user # Importar el modelo para que Base lo conozca

# --- Creación de Tablas (Opcional - Mejor usar Alembic) ---
try:
    user.Base.metadata.create_all(bind=database.engine)
    print("Tablas creadas (si no existían)")
except Exception as e:
    print(f"Error al crear tablas: {e}")
    # Considera añadir reintentos o esperar a que la BD esté disponible.

# --- Instancia de la Aplicación FastAPI ---
app = FastAPI(
    title="Microservicio de Usuarios (Hardcoded Config)",
    description="API para gestionar usuarios (con config. hardcodeada).",
    version="1.0.1",
)

# --- Incluir Routers ---
app.include_router(users.router)

# --- Ruta Raíz (Opcional) ---
@app.get("/", tags=["Root"])
async def read_root():
    """Ruta raíz simple para verificar que el servicio está funcionando."""
    return {"message": "Bienvenido al Microservicio de Usuarios (Hardcoded Config)"}

# --- Punto de entrada para Uvicorn ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)