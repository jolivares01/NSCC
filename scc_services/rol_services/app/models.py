from pydantic import BaseModel
from typing import List

class UserPermissions(BaseModel):
    id_rol: str
    paths: List[str]