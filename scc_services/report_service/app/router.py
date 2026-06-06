from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from .database import get_db_pool
from .models import ReportRequest, AgenteReportRequest
import pandas as pd
from io import BytesIO
import jwt
from datetime import datetime

# --- IMPORTACIÓN DEL CONFIGURADOR DE LOGS Y SETTINGS ---
from .core.config import settings
from api_gateway.utils.logger_config import setup_logger

# Inicialización del logger
log = setup_logger("REPORT-SERVICE")

router = APIRouter()

def get_token_info(request: Request):
    """Valida el JWT usando la SECRET_KEY centralizada en el .env"""
    auth_header = request.headers.get("Authorization") or request.headers.get("authorization")
    if not auth_header:
        log.error("Acceso denegado: Cabecera de autorización inexistente.")
        raise HTTPException(status_code=401, detail="Token inexistente")
    
    try:
        # Extraer token (soporta 'Bearer <token>' o solo '<token>')
        token = auth_header.split(" ")[1] if " " in auth_header else auth_header
        
        # Validación usando el objeto settings
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        log.error("El token ha expirado.")
        raise HTTPException(status_code=401, detail="El token ha expirado")
    except Exception as e:
        log.error(f"Error de validación de JWT: {str(e)}")
        raise HTTPException(status_code=401, detail="Token inválido")

def generate_excel_response(df_dict, filename):
    """Función auxiliar para generar el streaming del Excel con auto-ajuste"""
    log.info(f"Generando archivo Excel: {filename}.xlsx")
    output = BytesIO()
    try:
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for sheet_name, df in df_dict.items():
                if not df.empty:
                    log.debug(f"Procesando hoja: {sheet_name} con {len(df)} registros.")
                    
                    # Formatear fechas para Excel
                    for col in df.select_dtypes(include=['datetime64','datetime']).columns:
                        df[col] = df[col].dt.strftime('%d/%m/%Y %H:%M:%S')
                    
                    df.fillna('', inplace=True)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    # Auto-ajuste de columnas
                    worksheet = writer.sheets[sheet_name]
                    for idx, col in enumerate(df.columns):
                        series_max = df[col].astype(str).str.len().max()
                        max_len = max(series_max, len(str(col))) + 2
                        worksheet.set_column(idx, idx, min(max_len, 50))
        
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}.xlsx"}
        )
    except Exception as e:
        log.error(f"Fallo en la construcción del objeto Excel: {str(e)}", exc_info=True)
        raise e

# --- OPCIÓN 1: COMISIONES NORMALES ---
@router.post("/export-comisiones")
async def export_comisiones(request: Request, params: ReportRequest):
    db_pool = get_db_pool(request)
    user_data = get_token_info(request)
    login_usuario = user_data.get("sub")
    rol_usuario = user_data.get("role")
    
    log.info(f"EXPORTACIÓN: Usuario {login_usuario} ({rol_usuario}) solicita reporte de comisiones para periodo {params.periodo}")
    
    try:
        start_date_obj = datetime.strptime(f"{params.periodo}-01", "%Y-%m-%d").date()
    except Exception as e:
        log.error(f"Formato de periodo inválido: {params.periodo}")
        raise HTTPException(status_code=400, detail="Formato de fecha inválido")

    query_base = """
        SELECT 
            a.created_dt, a.order_number, a.gsm, a.type, a.operation_code, a.operation_type,
            b.display_value as plan_origen, b1.display_value as plan_destino,
            c.display_value as servicio_agregado, c1.display_value as servicio_removido,
            a.c2p_recharge, a.executive_agent, a.source_agent, a.locality, a.region,
            a.final_amount, a.period_id
        FROM scc_user.operations_history a
        LEFT JOIN scc_user.plans b on (a.origin_plan = b.id_plan)
        LEFT JOIN scc_user.plans b1 on (a.destination_plan = b1.id_plan)
        LEFT JOIN scc_user.services c on (a.added_service = c.id_service)
        LEFT JOIN scc_user.services c1 on (a.removed_service = c1.id_service)
        WHERE a.created_dt >= $1 
          AND a.created_dt < ($1 + interval '1 month')
          AND a.commissionable_flag = 'Y' 
          AND a.publish_flag = 'Y'
    """

    try:
        async with db_pool.acquire() as conn:
            # Si no es administrador, filtrar por su propio código de agente
            if rol_usuario != 'ROL_0001':
                log.debug(f"Aplicando filtro de agente para: {login_usuario}")
                query_agente = query_base + " AND a.source_agent = $2 "
                rows = await conn.fetch(query_agente, start_date_obj, login_usuario)
                name = "Mis_Comisiones"
            else:
                log.debug("Generando reporte global (Sábana)")
                rows = await conn.fetch(query_base, start_date_obj)
                name = "Sabana_Comisiones"

        if not rows:
            log.warning(f"Sin datos para {login_usuario} en el periodo {params.periodo}")
            raise HTTPException(status_code=404, detail="Sin datos para este periodo")
        
        return generate_excel_response(
            {name: pd.DataFrame([dict(r) for r in rows])}, 
            f"Comisiones_{params.periodo}"
        )
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        log.error(f"Error en consulta de exportación: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al procesar el reporte")

# --- OPCIÓN 2: COMISIONES ESPECIALES ---
@router.post("/export-especiales")
async def export_especiales(request: Request, params: ReportRequest):
    user_data = get_token_info(request)
    login_usuario = user_data.get("sub")
    
    if user_data.get("role") != 'ROL_0001':
        log.warning(f"Acceso denegado a Especiales: {login_usuario}")
        raise HTTPException(status_code=403, detail="No tiene permisos para este reporte")

    db_pool = get_db_pool(request)
    log.info(f"Exportando Especiales periodo {params.periodo}")
    
    try:
        year, month = params.periodo.split("-")
        periodo_id = f"{month}/{year}" 

        async with db_pool.acquire() as conn:
            query = "SELECT * FROM scc_user.special_commissions_history WHERE period_id = $1 ORDER BY 2"
            rows = await conn.fetch(query, periodo_id)

        if not rows:
            log.warning(f"Sin registros especiales para {periodo_id}")
            raise HTTPException(status_code=404, detail="Sin datos especiales para este periodo")
        
        return generate_excel_response(
            {"Especiales": pd.DataFrame([dict(r) for r in rows])}, 
            f"Especiales_{params.periodo}"
        )
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        log.error(f"Error exportando comisiones especiales: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno")
    
@router.post("/resumen-calculo")
async def get_resumen_calculo(request: Request, params: ReportRequest):
    db_pool = get_db_pool(request)
    user_data = get_token_info(request)
    login_usuario = user_data.get("sub")
    rol_usuario = user_data.get("role")
    
    log.info(f"RESUMEN: Usuario {login_usuario} solicita vista previa para periodo {params.periodo}")
    
    try:
        start_date_obj = datetime.strptime(f"{params.periodo}-01", "%Y-%m-%d").date()
    except Exception:
        raise HTTPException(status_code=400, detail="Formato de periodo inválido")

    # CAMBIO: Seleccionamos 'region' y quitamos 'operation_type'
    query_base = """
        SELECT 
            source_agent AS agente, 
            locality AS localidad, 
            region AS region, 
            COUNT(*) AS cantidad_ops,
            COALESCE(SUM(final_amount), 0) AS total_pagado
        FROM scc_user.operations_history 
        WHERE created_dt >= $1 
          AND created_dt < ($1 + interval '1 month')
          AND commissionable_flag = 'Y' 
          AND publish_flag = 'Y'
    """
    
    try:
        async with db_pool.acquire() as conn:
            if rol_usuario != 'ROL_0001':
                # Agrupamos por región (índice 3)
                query_final = query_base + " AND source_agent = $2 GROUP BY 1, 2, 3 ORDER BY 5 DESC"
                rows = await conn.fetch(query_final, start_date_obj, login_usuario)
            else:
                query_final = query_base + " GROUP BY 1, 2, 3 ORDER BY 5 DESC"
                rows = await conn.fetch(query_final, start_date_obj)

            return [dict(r) for r in rows]
            
    except Exception as e:
        log.error(f"Error en resumen-calculo: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al generar el resumen")
    
@router.post("/export-resumen-calculo")
async def export_resumen_calculo(request: Request, params: ReportRequest):
    db_pool = get_db_pool(request)
    user_data = get_token_info(request)
    login_usuario = user_data.get("sub")
    rol_usuario = user_data.get("role")
    
    log.info(f"EXPORT RESUMEN: Usuario {login_usuario} solicita Excel detallado para {params.periodo}")
    
    try:
        start_date_obj = datetime.strptime(f"{params.periodo}-01", "%Y-%m-%d").date()
    except Exception:
        raise HTTPException(status_code=400, detail="Formato de periodo inválido")

    # Mantenemos 'operation_type' y agregamos 'region'
    query_base = """
        SELECT 
            source_agent AS "AGENTE", 
            locality AS "LOCALIDAD",
            region AS "REGION", 
            operation_type AS "TIPO OPERACION", 
            COUNT(*) AS "CANTIDAD OPS",
            COALESCE(SUM(final_amount), 0) AS "TOTAL PAGADO"
        FROM scc_user.operations_history 
        WHERE created_dt >= $1 
          AND created_dt < ($1 + interval '1 month')
          AND commissionable_flag = 'Y' 
          AND publish_flag = 'Y'
    """

    try:
        async with db_pool.acquire() as conn:
            if rol_usuario != 'ROL_0001':
                # Agrupamos por los 4 campos descriptivos
                query_final = query_base + " AND source_agent = $2 GROUP BY 1, 2, 3, 4 ORDER BY 1, 4"
                rows = await conn.fetch(query_final, start_date_obj, login_usuario)
            else:
                query_final = query_base + " GROUP BY 1, 2, 3, 4 ORDER BY 1, 4"
                rows = await conn.fetch(query_final, start_date_obj)

        if not rows:
            raise HTTPException(status_code=404, detail="Sin datos para exportar")

        # Generamos el DataFrame con la estructura completa
        df = pd.DataFrame([dict(r) for r in rows])
        
        return generate_excel_response(
            {"Resumen_Detallado": df}, 
            f"Resumen_Calculo_{params.periodo}"
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        log.error(f"Error exportando resumen con región: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al generar el archivo")
    

@router.post("/incentivos-ventas")
async def get_incentivos_ventas(request: Request, params: ReportRequest):
    db_pool = get_db_pool(request)
    user_data = get_token_info(request)
    login_usuario = user_data.get("sub")
    rol_usuario = user_data.get("role")
    
    log.info(f"INCENTIVOS: Consulta vista previa para {params.periodo}")
    
    # 1. Convertimos a DATE para que coincida con el nuevo SP
    try:
        start_date_obj = datetime.strptime(f"{params.periodo}-01", "%Y-%m-%d").date()
    except Exception:
        raise HTTPException(status_code=400, detail="Formato de periodo inválido")

    try:
        async with db_pool.acquire() as conn:
            # 2. Llamada con casting explícito ::DATE
            query = "SELECT * FROM scc_user.sp_incentives($1::DATE, $2)"
            rows = await conn.fetch(query, start_date_obj, 'OT-001')

            if not rows:
                return []

            res = [dict(r) for r in rows]
            if rol_usuario != 'ROL_0001':
                res = [r for r in res if r['source_agent'] == login_usuario]

            return res

    except Exception as e:
        log.error(f"Error en vista previa incentivos: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error en base de datos: {str(e)}")

@router.post("/export-incentivos")
async def export_incentivos(request: Request, params: ReportRequest):
    db_pool = get_db_pool(request)
    user_data = get_token_info(request)
    login_usuario = user_data.get("sub")
    
    try:
        start_date_obj = datetime.strptime(f"{params.periodo}-01", "%Y-%m-%d").date()
        
        async with db_pool.acquire() as conn:
            # 3. Llamada con casting explícito ::DATE
            rows = await conn.fetch(
                "SELECT * FROM scc_user.sp_incentives($1::DATE, $2)", 
                start_date_obj, 
                'OT-001'
            )
            
            if not rows:
                raise HTTPException(status_code=404, detail="No hay incentivos para este periodo")

            df = pd.DataFrame([dict(r) for r in rows])
            
            if user_data.get("role") != 'ROL_0001':
                df = df[df['source_agent'] == login_usuario]

            return generate_excel_response(
                {"Incentivos_Ventas": df}, 
                f"Incentivos_{params.periodo}"
            )
            
    except HTTPException as he:
        raise he
    except Exception as e:
        log.error(f"Error exportando incentivos: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al generar reporte: {str(e)}")
    
@router.post("/export-monto-fijo")
async def export_monto_fijo(request: Request, params: ReportRequest):
    db_pool = get_db_pool(request)
    user_data = get_token_info(request)
    login_usuario = user_data.get("sub")
    rol_usuario = user_data.get("role")
    
    log.info(f"EXPORT MONTO FIJO: Usuario {login_usuario} solicita reporte para {params.periodo}")
    
    try:
        # Convertimos el periodo 'YYYY-MM' a fecha 'YYYY-MM-01'
        start_date_obj = datetime.strptime(f"{params.periodo}-01", "%Y-%m-%d").date()
    except Exception:
        raise HTTPException(status_code=400, detail="Periodo inválido")

    try:
        async with db_pool.acquire() as conn:
            # Llamamos al Stored Procedure
            query = "SELECT * FROM scc_user.sp_monto_fijo($1)"
            
            # Si no es admin, filtramos el resultado del SP por su usuario
            if rol_usuario != 'ROL_0001':
                query += " WHERE source_agent = $2"
                rows = await conn.fetch(query, start_date_obj, login_usuario)
            else:
                rows = await conn.fetch(query, start_date_obj)

        if not rows:
            raise HTTPException(status_code=404, detail="No hay datos para este periodo")

        # Convertimos a DataFrame para el Excel
        df = pd.DataFrame([dict(r) for r in rows])
        
        # Renombramos columnas para que el Excel se vea profesional
        df.columns = ['AGENTE', 'LOCALIDAD', 'DESCRIPCION', 'PERIODO', 'TIPO USUARIO', 'MONTO CANCELAR']

        return generate_excel_response(
            {"Monto_Fijo_Postventa": df}, 
            f"Reporte_Monto_Fijo_{params.periodo}"
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        log.error(f"Error en export-monto-fijo: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al procesar el reporte de monto fijo")
    
# --- NUEVA OPCIÓN: CONSULTA INDIVIDUALIZADA SOLICITADA POR FINANZAS ---
@router.post("/comisiones-agente")
async def get_comisiones_agente_total(request: Request, params: AgenteReportRequest):
    db_pool = get_db_pool(request)
    user_data = get_token_info(request)
    login_usuario = user_data.get("sub")
    rol_usuario = user_data.get("role")
    
    log.info(f"CONSULTA MENSUAL: Usuario {login_usuario} ({rol_usuario}) solicita periodo Front: {params.periodo}")
    
    # === SOLUCIÓN COMPLETA DE SEGURIDAD Y CONTEXTO ===
    # Si es administrador y escribió algo en la barra, lo usamos.
    if rol_usuario == 'ROL_0001' and params.source_agent and params.source_agent.strip():
        agente_a_consultar = params.source_agent.strip()
    else:
        # Si es un Agente Autorizado (o el campo vino vacío), forzamos su propio login extraído del Token JWT
        agente_a_consultar = login_usuario.strip()

    try:
        ano_int, mes_int = map(int, params.periodo.split("-"))
    except Exception:
        raise HTTPException(status_code=400, detail="Formato de periodo inválido.")

    try:
        async with db_pool.acquire() as conn:
            query = """
                SELECT concepto, comision 
                FROM scc_user.sp_consulta_comisiones_por_mes($1, $2, $3);
            """
            rows = await conn.fetch(query, ano_int, mes_int, agente_a_consultar)

            if not rows:
                log.warning(f"Sin registros en {ano_int}-{mes_int} para el agente {agente_a_consultar}")
                return []

            # Retornamos la data limpia. Incluimos el agente real en la respuesta para que el Front lo pinte
            # sin importar si no lo conocía desde el LocalStorage.
            return [dict(r) for r in rows]

    except Exception as e:
        log.error(f"Error crítico en sp_consulta_comisiones_por_mes: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno al procesar comisiones.")