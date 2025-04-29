from fastapi import APIRouter, Depends, HTTPException, status
import redis.asyncio as redis
from typing import Dict

from microservice_metrics.app.db.database import get_redis_client
from microservice_metrics.app.schemas.metric import Metric, AllMetrics
from microservice_metrics.app.services import metric_service

router = APIRouter(
    prefix="/metrics",
    tags=["metrics"],
    responses={500: {"description": "Internal server error"}},
)

@router.post("/increment/{metric_name}", response_model=Metric, summary="Increment a metric counter")
async def increment_counter(
    metric_name: str,
    increment_by: int = 1, # Permitir incrementar por más de 1 (opcional)
    client: redis.Redis = Depends(get_redis_client)
):
    """
    Incrementa el contador para una métrica dada.
    Devuelve el nombre de la métrica y su nuevo valor.
    """
    try:
        new_value = await metric_service.increment_metric(client, metric_name, increment_by)
        return Metric(name=metric_name, value=new_value)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/value/{metric_name}", response_model=Metric, summary="Get the value of a specific metric")
async def get_single_metric(
    metric_name: str,
    client: redis.Redis = Depends(get_redis_client)
):
    """
    Obtiene el valor actual de una métrica específica.
    Devuelve 404 si la métrica no existe.
    """
    try:
        value = await metric_service.get_metric_value(client, metric_name)
        if value is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Métrica '{metric_name}' no encontrada.")
        return Metric(name=metric_name, value=value)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/all", response_model=AllMetrics, summary="Get all metrics and their values")
async def get_all_metrics_values(
    client: redis.Redis = Depends(get_redis_client)
):
    """
    Obtiene un diccionario con todas las métricas y sus valores actuales.
    ¡Precaución! Puede ser lento en bases de datos Redis con muchas claves.
    """
    try:
        all_metrics_dict = await metric_service.get_all_metrics(client)
        return AllMetrics(metrics=all_metrics_dict)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))