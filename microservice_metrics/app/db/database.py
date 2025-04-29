import redis.asyncio as redis
import os

# --- URL Hardcodeada para Redis ---
# ¡ADVERTENCIA! No recomendable para producción.
# Usa el nombre del servicio definido en docker-compose.yml o Kubernetes
REDIS_HOST = "redis-db" # Nombre del servicio Redis
REDIS_PORT = 6379
REDIS_DB_NUMBER = 0 # Número de la base de datos Redis a usar (0 por defecto)
# REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_NUMBER}" # Alternativa en formato URL
# ----------------------------------

class RedisDB:
    client: redis.Redis = None

redis_db = RedisDB()

async def connect_to_redis():
    """Establece la conexión con Redis al iniciar la aplicación."""
    print(f"Intentando conectar a Redis en {REDIS_HOST}:{REDIS_PORT} (DB {REDIS_DB_NUMBER})...")
    try:
        # Crear pool de conexiones asíncrono
        redis_db.client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB_NUMBER,
            decode_responses=True # Decodificar respuestas de bytes a strings automáticamente
        )
        # Verificar conexión
        await redis_db.client.ping()
        print("Conexión a Redis establecida exitosamente.")
    except Exception as e:
        print(f"Error al conectar a Redis: {e}")
        redis_db.client = None
        # Considerar si la app debe fallar si no conecta
        raise e

async def close_redis_connection():
    """Cierra la conexión con Redis al detener la aplicación."""
    if redis_db.client:
        print("Cerrando conexión con Redis...")
        await redis_db.client.aclose() # Usar aclose() para async
        print("Conexión a Redis cerrada.")

def get_redis_client() -> redis.Redis:
    """Dependencia para obtener el cliente Redis."""
    if redis_db.client is None:
        # Esto no debería pasar si el lifespan funciona, pero como fallback
        raise Exception("Cliente Redis no inicializado. La aplicación no se inició correctamente.")
    return redis_db.client