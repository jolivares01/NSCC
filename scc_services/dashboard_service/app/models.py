from pydantic import BaseModel
from typing import Optional

class FiltroOperaciones(BaseModel):
    # 'ventas' o 'postventas' para decidir la tabla
    tipo_operacion: str 
    # Rango de fechas para filtrar la consulta
    fecha_inicio: str 
    fecha_fin: str