# app/models.py

from pydantic import BaseModel
from typing import Optional

class RegistroUsuario(BaseModel):
    region: str
    localidad: str
    username: str
    rol: str
    createdBy: str
    origin_type: str              # 'INTERNO' o 'EXTERNO'
    user_type: Optional[str] = None    # id_type de scc_user.user_type
    id_channel: Optional[str] = None   # id_channel de scc_user.user_channel

class ActualizarUsuario(BaseModel):
    id_region: int
    location_name: str
    id_rol: str
    is_active: bool
    changedBy: str
    user_type: Optional[str] = None
    id_channel: Optional[str] = None