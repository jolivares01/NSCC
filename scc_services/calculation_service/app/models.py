from pydantic import BaseModel
from typing import List, Dict

class ParametrosCalculo(BaseModel):
    period_id: str
    amount: str  

class SummaryItem(BaseModel):
    operation_type: str
    total: int

class CalculationResponse(BaseModel):
    status: str
    mensaje: str
    reporte: List[SummaryItem]