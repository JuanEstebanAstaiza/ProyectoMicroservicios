from pydantic import BaseModel
from typing import Dict

class Metric(BaseModel):
    """Representa una métrica con su nombre y valor."""
    name: str
    value: int

class AllMetrics(BaseModel):
    """Representa un diccionario con todas las métricas."""
    metrics: Dict[str, int]