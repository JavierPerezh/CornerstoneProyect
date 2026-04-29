from typing import List

from pydantic import BaseModel


class ProgresoResumen(BaseModel):
    periodo: str
    total_interacciones: int
    alertas: dict
    riesgo_promedio: float
    sintomas_madre_frecuentes: List[dict]
    sintomas_bebe_frecuentes: List[dict]
    acciones_inmediatas: int


class DatoGrafico(BaseModel):
    labels: List[str]
    datasets: List[dict]
    riesgo_promedio: List[float]
