from fastapi import APIRouter, HTTPException, Request, Query
from .database import get_db_pool
from datetime import datetime
# --- IMPORTACIÓN DEL CONFIGURADOR DE LOGS ---
from api_gateway.utils.logger_config import setup_logger

from .models import (
    PlanRuleUpdate, 
    ServiceRuleUpdate, 
    GeneralRuleUpdate, 
    NewPlanCommission, 
    NewServiceCommission,
    NewBusinessRule
)

# Inicialización del logger para este servicio
log = setup_logger("BUSINESS-RULES")

router = APIRouter()

@router.get("/plans")
async def get_plan_rules(request: Request):
    db_pool = get_db_pool(request)
    log.debug("Consultando lista de planes comisionables.")
    query = """
        SELECT 
            a.id_plan,
            a.display_value as plan_name,
            a.id_instance_type,
            b.display_value as instance_name,
            a.amount_to_pay,
            a.amount_percentage,
            a.channel,
            a.inactive_dt
        FROM scc_user.commissionable_plans a 
        INNER JOIN scc_user.instance_type b ON (a.id_instance_type = b.id_instance_type)
        ORDER BY a.display_value, a.channel
    """
    try:
        async with db_pool.acquire() as conn:
            data = await conn.fetch(query)
            log.info(f"Consulta de planes exitosa. Registros obtenidos: {len(data)}")
            return data
    except Exception as e:
        log.error(f"Error al obtener planes comisionables: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al consultar la base de datos")

@router.put("/plans/update")
async def update_plan_rule(request: Request, data: PlanRuleUpdate):
    db_pool = get_db_pool(request)
    log.debug(f"Petición de actualización de plan recibida: {data.dict()}")
    
    inactive_value = None if getattr(data, 'is_active', True) else datetime.now()
    
    try:
        async with db_pool.acquire() as conn:
            query = """
                UPDATE scc_user.commissionable_plans 
                SET amount_to_pay = $1, 
                    amount_percentage = $2, 
                    change_dt = NOW(), 
                    change_who = $3,
                    inactive_dt = $4
                WHERE id_plan = $5 
                  AND id_instance_type = $6 
                  AND channel = $7
            """
            await conn.execute(query, 
                               data.amount_to_pay, 
                               data.amount_percentage, 
                               data.change_who, 
                               inactive_value, 
                               data.id_plan, 
                               data.id_instance_type, 
                               data.channel)
            log.info(f"Plan {data.id_plan} actualizado por {data.change_who}. Estado activo: {data.is_active}")
            return {"status": "OK", "message": "Registro de plan actualizado"}
    except Exception as e:
        log.error(f"Fallo al actualizar plan {data.id_plan}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno al actualizar plan")

@router.get("/services")
async def get_service_rules(request: Request):
    db_pool = get_db_pool(request)
    log.debug("Consultando lista de servicios comisionables.")
    query = """
        SELECT 
            id_service, 
            display_value, 
            amount_to_pay, 
            amount_percentage, 
            channel,
            inactive_dt 
        FROM scc_user.commissionable_services 
        ORDER BY display_value, channel
    """
    try:
        async with db_pool.acquire() as conn:
            data = await conn.fetch(query)
            log.info(f"Consulta de servicios exitosa. Registros obtenidos: {len(data)}")
            return data
    except Exception as e:
        log.error(f"Error al obtener servicios comisionables: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al consultar servicios")

@router.put("/services/update")
async def update_service_rule(request: Request, data: ServiceRuleUpdate):
    db_pool = get_db_pool(request)
    log.debug(f"Petición de actualización de servicio recibida: {data.dict()}")
    
    inactive_value = None if getattr(data, 'is_active', True) else datetime.now()
    
    try:
        async with db_pool.acquire() as conn:
            query = """
                UPDATE scc_user.commissionable_services 
                SET amount_to_pay = $1, 
                    amount_percentage = $2, 
                    change_dt = NOW(), 
                    change_who = $3,
                    inactive_dt = $4
                WHERE id_service = $5 
                  AND channel = $6
            """
            await conn.execute(
                query, 
                data.amount_to_pay, 
                data.amount_percentage, 
                data.change_who, 
                inactive_value, 
                data.id_service, 
                data.channel
            )
            log.info(f"Servicio {data.id_service} actualizado por {data.change_who}. Estado activo: {data.is_active}")
            return {"status": "OK", "message": "Línea de servicio actualizada"}
    except Exception as e:
        log.error(f"Fallo al actualizar servicio {data.id_service}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno al actualizar servicio")

@router.get("/general-rules")
async def get_general_rules(request: Request):
    db_pool = get_db_pool(request)
    log.debug("Consultando reglas generales de negocio.")
    query = """
        SELECT 
            b.display_value as operation_name,
            a.operation_code,
            a.amount_to_pay,
            a.amount_percentege,
            a.origin_plan_pattern,
            a.destination_plan_pattern,
            a.commissionable_flag,
            a.rule_type,
            a.description
        FROM scc_user.commissionable_rules a
        INNER JOIN scc_user.order_types b ON (a.operation_code = b.id_order_type)
        ORDER BY a.operation_code, a.rule_type
    """
    try:
        async with db_pool.acquire() as conn:
            data = await conn.fetch(query)
            log.info(f"Consulta de reglas generales exitosa. Total: {len(data)}")
            return data
    except Exception as e:
        log.error(f"Fallo al consultar reglas generales: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error de servidor")

@router.put("/general-rules/update")
async def update_general_rule(request: Request, data: GeneralRuleUpdate):
    db_pool = get_db_pool(request)
    log.debug(f"Intentando actualizar regla lógica. Datos: {data.dict()}")
    try:
        async with db_pool.acquire() as conn:
            query = """
                UPDATE scc_user.commissionable_rules 
                SET amount_to_pay = $1, 
                    amount_percentege = $2, 
                    origin_plan_pattern = $3,
                    destination_plan_pattern = $4,
                    commissionable_flag = $5,
                    description = $6
                WHERE operation_code = $7 
                  AND rule_type = $8
                  AND description = $9
            """
            await conn.execute(
                query, 
                data.amount_to_pay, 
                data.amount_percentege, 
                data.origin_plan_pattern, 
                data.destination_plan_pattern,
                data.commissionable_flag, 
                data.description,
                data.operation_code, 
                data.rule_type, 
                data.description_original
            )
            log.info(f"Regla {data.operation_code} actualizada exitosamente.")
            return {"status": "OK", "message": "Regla actualizada"}
    except Exception as e:
        log.error(f"Fallo en UPDATE de regla {data.operation_code}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al actualizar regla")

@router.get("/catalog/plans")
async def get_master_plans(request: Request):
    db_pool = get_db_pool(request)
    log.debug("Cargando catálogo maestro de planes.")
    async with db_pool.acquire() as conn:
        return await conn.fetch("SELECT id_plan, display_value, id_instance_type FROM scc_user.plans ORDER BY 2")

@router.get("/catalog/services")
async def get_master_services(request: Request):
    db_pool = get_db_pool(request)
    log.debug("Cargando catálogo maestro de servicios.")
    async with db_pool.acquire() as conn:
        return await conn.fetch("SELECT id_service, display_value FROM scc_user.services ORDER BY 2")

@router.get("/catalog/channels")
async def get_channels(request: Request):
    db_pool = get_db_pool(request)
    log.debug("Cargando catálogo de canales autorizados.")
    async with db_pool.acquire() as conn:
        return await conn.fetch("SELECT id_channel FROM scc_user.user_channel")

@router.post("/plans/create")
async def create_plan_commission(request: Request, data: NewPlanCommission):
    db_pool = get_db_pool(request)
    log.debug(f"Insertando nuevo plan en comisiones: {data.id_plan}")
    try:
        async with db_pool.acquire() as conn:
            query = """
                INSERT INTO scc_user.commissionable_plans 
                (id_plan, display_value, id_instance_type, amount_to_pay, type_pay, channel, created_dt, created_who, active_dt, change_dt, change_who, inactive_dt, amount_percentage, division)
                VALUES ($1, $2, $3, $4, 'USD', $5, NOW(), $6, NOW(), NOW(), $6, NULL, $7, '100')
            """
            await conn.execute(query, data.id_plan, data.display_value, data.id_instance_type, data.amount_to_pay, data.channel, data.created_who, data.amount_percentage)
            log.info(f"Nuevo plan comisionable creado: {data.id_plan} por {data.created_who}")
        return {"status": "OK"}
    except Exception as e:
        log.error(f"Fallo al insertar plan {data.id_plan}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="El plan ya existe en comisiones para ese canal")

@router.post("/services/create")
async def create_service_commission(request: Request, data: NewServiceCommission):
    db_pool = get_db_pool(request)
    log.debug(f"Insertando nuevo servicio en comisiones: {data.id_service}")
    try:
        async with db_pool.acquire() as conn:
            query = """
                INSERT INTO scc_user.commissionable_services 
                (id_service, display_value, amount_to_pay, type_pay, channel, created_dt, created_who, active_dt, change_dt, change_who, inactive_dt, amount_percentage, division)
                VALUES ($1, $2, $3, 'USD', $4, NOW(), $5, NOW(), NOW(), $5, NULL, $6, '100')
            """
            await conn.execute(query, data.id_service, data.display_value, data.amount_to_pay, data.channel, data.created_who, data.amount_percentage)
            log.info(f"Nuevo servicio comisionable creado: {data.id_service} por {data.created_who}")
        return {"status": "OK"}
    except Exception as e:
        log.error(f"Fallo al insertar servicio {data.id_service}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="El servicio ya existe en comisiones")

@router.get("/catalog/order-types")
async def get_order_types(request: Request):
    db_pool = get_db_pool(request)
    log.debug("Cargando catálogo de tipos de órdenes.")
    async with db_pool.acquire() as conn:
        return await conn.fetch("SELECT id_order_type, display_value FROM scc_user.order_types ORDER BY display_value")

@router.post("/general-rules/create")
async def create_general_rule(request: Request, data: NewBusinessRule):
    db_pool = get_db_pool(request)
    log.debug(f"CONSTRUCTOR: Generando regla para OT: {data.operation_code}. Origen: {data.origin_plan_pattern}, Destino: {data.destination_plan_pattern}")
    try:
        async with db_pool.acquire() as conn:
            query = """
                INSERT INTO scc_user.commissionable_rules 
                (operation_code, amount_to_pay, amount_percentege, description, 
                 origin_plan_pattern, destination_plan_pattern, commissionable_flag, rule_type)
                VALUES ($1, $2, $3, $4, $5, $6, $7, 'PLAN_RULE')
            """
            await conn.execute(query, data.operation_code, data.amount_to_pay, 
                               data.amount_percentage, data.description,
                               data.origin_plan_pattern, data.destination_plan_pattern, 
                               data.commissionable_flag)
            log.info(f"Nueva Regla Lógica registrada para OT {data.operation_code}.")
        return {"status": "OK"}
    except Exception as e:
        log.error(f"Fallo al crear Regla Lógica: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Error en los datos de la regla o duplicidad")