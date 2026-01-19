from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ClaimCreate(BaseModel):
    agente: str
    desc_claims: str

class InteractionCreate(BaseModel):
    id_inc_claims: str
    user_response_message: str
    admin_user: str 