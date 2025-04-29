
# Script para inicializar la base de datos MongoDB para el microservicio de contenido.
# Asegura que la BD y la colección existen y crea índices definidos en el modelo Beanie.

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

# Importa tu modelo Beanie (ajusta la ruta si es necesario)
# Asume que puedes importar desde la estructura del microservicio
try:
    from microservice_content.app.schemas.content import ContentItem
except ImportError:
    print("Asegúrate de ejecutar este script desde un entorno donde")
    print("se pueda importar 'microservice_content.app.schemas.content'")
    # Alternativa: Redefinir una versión mínima del modelo aquí si es necesario
    # O ajustar PYTHONPATH al ejecutar el script.
    exit(1)


# --- Configuración de Conexión (Hardcodeada) ---
MONGO_URL = "mongodb://localhost:27017/"
DATABASE_NAME = "content_db_async" # Debe coincidir con la de tu app
# ---------------------------------------------

async def initialize_mongo():
    """Conecta, inicializa Beanie y crea índices."""
    print(f"Conectando a MongoDB en {MONGO_URL}...")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DATABASE_NAME]
    print(f"Usando base de datos: {DATABASE_NAME}")

    try:
        # Verificar conexión
        await client.admin.command('ping')
        print("Conexión exitosa.")

        print("Inicializando Beanie para asegurar índices...")
        # Inicializa Beanie solo con el propósito de crear los índices
        # definidos en ContentItem.Settings.indexes
        await init_beanie(database=db, document_models=[ContentItem])

        print(f"Índices para la colección '{ContentItem.Settings.name}' asegurados (creados si no existían).")

        # Opcional: Insertar un documento de ejemplo si la colección está vacía
        collection = db[ContentItem.Settings.name]
        count = await collection.count_documents({})
        if count == 0:
            print("Colección vacía. Insertando documento de ejemplo...")
            example_doc = {
                "title": "Documento Inicial",
                "body": "Este documento fue creado por el script de inicialización.",
                "tags": ["init", "example"],
                "created_at": asyncio.get_event_loop().time(), # Usar tiempo del loop
                 "updated_at": asyncio.get_event_loop().time()
            }
            await collection.insert_one(example_doc)
            print("Documento de ejemplo insertado.")
        else:
            print(f"La colección '{ContentItem.Settings.name}' ya contiene documentos ({count}).")


    except Exception as e:
        print(f"Error durante la inicialización de MongoDB: {e}")
    finally:
        print("Cerrando conexión.")
        client.close()

if __name__ == "__main__":
    print("--- Iniciando Script de Inicialización MongoDB ---")
    # Ejecutar la función asíncrona
    asyncio.run(initialize_mongo())
    print("--- Script de Inicialización MongoDB Finalizado ---")