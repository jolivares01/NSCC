from pydantic import BaseModel

class ReportRequest(BaseModel):
    periodo: str  # Ejemplo: "2026-02"

class AgenteReportRequest(BaseModel):
    periodo: str       # Recibe 'YYYY-MM'
    source_agent: str  # Recibe el código de agente o localidad (ej: 'CAR_64598_1')