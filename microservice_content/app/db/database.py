from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import os

# Importar el modelo de documento Beanie
from microservice_content.app.schemas.content import ContentItem # Ahora ContentItem es el Document

# --- URL Hardcodeada para MongoDB ---
# Usa el nombre del servicio definido en docker-compose.yml o Kubernetes
MONGO_DATABASE_URL = "mongodb://mongo-db:27017/"
#                              ^^^^^^^^ (Nombre del servicio de la BD Mongo)
DATABASE_NAME = "content_db_async"
# ----------------------------------

async def init_db():
    """Inicializa la conexión con MongoDB y Beanie."""
    print(f"Intentando conectar a MongoDB en {MONGO_DATABASE_URL}...")
    client = AsyncIOMotorClient(MONGO_DATABASE_URL)
    db = client[DATABASE_NAME]

    try:
         # Verificar conexión
        await client.admin.command('ping')
        print("Conexión a MongoDB establecida exitosamente.")
        print(f"Inicializando Beanie con base de datos: {DATABASE_NAME}")

        # Inicializar Beanie con los modelos Document que definiste
        await init_beanie(database=db, document_models=[ContentItem])

        print("Beanie inicializado correctamente.")
        # Puedes añadir más modelos a la lista document_models si tienes otros
        # ej: await init_beanie(database=db, document_models=[ContentItem, Author, ...])

    except Exception as e:
        print(f"Error al inicializar la base de datos o Beanie: {e}")
        # Considera si la aplicación debe detenerse si falla la conexión
        raise e # Re-lanzar para que el lifespan falle si es necesario

# Nota: Beanie/Motor manejan el pool de conexiones. No necesitamos get_db o close explícito aquí.
# La conexión se establece al inicio y se mantiene.