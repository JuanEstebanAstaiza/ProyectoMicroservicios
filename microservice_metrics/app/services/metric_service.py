import redis.asyncio as redis
from typing import Dict, Optional

# Nota: Redis es principalmente clave-valor, no usamos modelos complejos aquí.

async def increment_metric(client: redis.Redis, metric_name: str, increment_by: int = 1) -> int:
    """Incrementa el valor de una métrica en Redis. Devuelve el nuevo valor."""
    try:
        # INCRBY es atómico, ideal para contadores
        new_value = await client.incrby(metric_name, increment_by)
        return new_value
    except Exception as e:
        print(f"Error al incrementar métrica '{metric_name}' en Redis: {e}")
        # Podrías lanzar una excepción HTTP aquí si lo llamas desde la API
        raise

async def get_metric_value(client: redis.Redis, metric_name: str) -> Optional[int]:
    """Obtiene el valor de una métrica específica de Redis."""
    try:
        value = await client.get(metric_name)
        if value is not None:
            try:
                return int(value) # Redis devuelve strings, convertir a int
            except ValueError:
                print(f"Valor para métrica '{metric_name}' no es un entero válido en Redis: {value}")
                return None # O manejar el error de otra forma
        return None # La métrica no existe
    except Exception as e:
        print(f"Error al obtener métrica '{metric_name}' de Redis: {e}")
        raise

async def get_all_metrics(client: redis.Redis) -> Dict[str, int]:
    """Obtiene todas las métricas (claves) y sus valores de Redis."""
    # ¡Precaución! KEYS puede ser lento en bases de datos Redis grandes.
    # En producción, considera usar SCAN o mantener un set separado con los nombres de las métricas.
    all_metrics = {}
    try:
        metric_names = await client.keys('*') # Obtener todas las claves (¡Cuidado!)
        for name in metric_names:
            value = await get_metric_value(client, name)
            if value is not None:
                all_metrics[name] = value
        return all_metrics
    except Exception as e:
        print(f"Error al obtener todas las métricas de Redis: {e}")
        raise