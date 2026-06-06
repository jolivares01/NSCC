from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PlanRuleUpdate(BaseModel):
    id_plan: str
    id_instance_type: str # Nuevo: para identificar la instancia
    channel: str          # Nuevo: para identificar el canal
    amount_to_pay: str
    amount_percentage: Optional[str] = None
    change_who: str
    is_active: Optional[bool] = True

class ServiceRuleUpdate(BaseModel):
    id_service: str
    channel: str # Requerido para identificar la fila única
    amount_to_pay: str
    amount_percentage: Optional[str] = None
    change_who: str
    is_active: Optional[bool] = True

class GeneralRuleUpdate(BaseModel):
    operation_code: str
    rule_type: str
    amount_to_pay: Optional[str] = None
    amount_percentege: Optional[str] = None
    description: Optional[str] = None
    description_original: str  
    origin_plan_pattern: Optional[str] = None
    destination_plan_pattern: Optional[str] = None
    commissionable_flag: str

class NewPlanCommission(BaseModel):
    id_plan: str
    display_value: str
    id_instance_type: str
    amount_to_pay: str
    channel: str
    amount_percentage: str
    created_who: str

class NewServiceCommission(BaseModel):
    id_service: str
    display_value: str
    amount_to_pay: str
    channel: str
    amount_percentage: str
    created_who: str

class NewBusinessRule(BaseModel):
    operation_code: str
    amount_to_pay: Optional[str] = None
    amount_percentage: Optional[str] = None
    description: str
    origin_plan_pattern: str
    destination_plan_pattern: str
    commissionable_flag: str = 'Y'