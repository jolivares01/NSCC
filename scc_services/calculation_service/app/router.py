from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Body
from fastapi.responses import StreamingResponse 
from .database import get_db_pool
from .models import CalculationResponse, ParametrosCalculo
from io import BytesIO
import pandas as pd
import asyncio 
import oracledb 
from .core.config import settings
from api_gateway.utils.logger_config import setup_logger
from datetime import datetime

# Inicialización del logger
log = setup_logger("CALCULATION-SERVICE")

router = APIRouter()

# --- CARGA DE COMISIONES ESPECIALES ---
@router.post("/special-commissions/upload", name="upload_special_commissions")
async def upload_special_commissions(request: Request, file: UploadFile = File(...)):
    db_pool = get_db_pool(request)
    log.info(f"Iniciando carga de archivo: {file.filename}")
    
    if not file.filename.endswith('.txt'):
        log.error(f"Extensión no válida: {file.filename}")
        raise HTTPException(status_code=400, detail="Solo se permiten archivos .txt")
    
    try:
        content = await file.read()
        decoded_content = content.decode('utf-8')
        lines = decoded_content.splitlines()
        log.debug(f"Archivo leído: {len(lines)} líneas.")
        
        records = []
        for i, line in enumerate(lines):
            if not line.strip(): continue
            parts = line.split('{')
            if len(parts) >= 6:
                try:
                    records.append((
                        int(parts[0]), parts[1], parts[2], parts[3], parts[4], int(parts[5]), 
                        parts[6] if len(parts) > 6 else ""
                    ))
                except (ValueError, IndexError):
                    log.debug(f"Línea {i+1} ignorada por error de formato.")
                    continue

        if not records:
            log.error("No se encontraron registros válidos en el TXT.")
            raise HTTPException(status_code=400, detail="El archivo no contiene registros válidos.")

        async with db_pool.acquire() as conn:
            async with conn.transaction():
                log.info("Limpiando tabla temporal e insertando nuevos registros especiales.")
                await conn.execute("TRUNCATE TABLE scc_user.special_commissions")
                query_insert = """
                    INSERT INTO scc_user.special_commissions 
                    (codigo, login, period_id, amount, description, commission_type, att1)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """
                await conn.executemany(query_insert, records)
                
                await conn.execute("""
                    INSERT INTO scc_user.special_commissions_history 
                    (codigo, login, period_id, amount, description, commission_type, att1)
                    SELECT codigo, login, period_id, amount, description, commission_type, 
                            to_char(CURRENT_TIMESTAMP, 'YYYY-MM-DD HH24:MI:SS')
                    FROM scc_user.special_commissions
                """)
                log.info("Registros especiales procesados y guardados en historial.")
            
        return {"status": "EXITO", "message": f"Se procesaron {len(records)} registros."}

    except Exception as e:
        log.error(f"Error en upload_special_commissions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# --- EJECUCIÓN DE CÁLCULO ---
@router.post("/ejecutar-calculo", response_model=CalculationResponse)
async def ejecutar_proceso_calculo(request: Request, params: ParametrosCalculo):
    db_pool = get_db_pool(request)
    log.info(f"SOLICITUD DE CÁLCULO: Periodo {params.period_id}")
    
    async with db_pool.acquire() as conn:
        existe = await conn.fetchval("SELECT 1 FROM scc_user.commission_multiplication WHERE period_id = $1 LIMIT 1", params.period_id)
        if existe:
            log.error(f"El periodo {params.period_id} ya fue procesado anteriormente.")
            raise HTTPException(status_code=400, detail={"mensaje": "Periodo ya procesado."})

        async with conn.transaction():
            try:
                log.debug("Actualizando parámetros de multiplicación.")
                await conn.execute("UPDATE scc_user.commission_multiplication SET inactive_dt = CURRENT_TIMESTAMP WHERE inactive_dt IS NULL")
                await conn.execute("INSERT INTO scc_user.commission_multiplication (period_id, amount, created_who) VALUES ($1, $2, 'JOLIVARES')", params.period_id, params.amount)

                # Ejecución de SPs
                log.info("Ejecutando Procedimientos Almacenados del Motor...")
                await conn.execute("CALL scc_user.sp_insert_operations_tmp()", timeout=300)
                await conn.execute("CALL scc_user.sp_motor_calculo()", timeout=300)
                await conn.execute("CALL scc_user.sp_operaciones_comisionables()", timeout=300)

                query_reporte = """
                    SELECT operation_type, COUNT(*)::int AS total
                    FROM scc_user.operations_tmp WHERE commissionable_flag = 'Y'
                    GROUP BY operation_type ORDER BY total DESC;
                """
                resultados = await conn.fetch(query_reporte)
                log.info(f"Proceso de cálculo finalizado exitosamente para {params.period_id}")
                return {"status": "EXITO", "mensaje": "Proceso culminado", "reporte": [dict(r) for r in resultados]}

            except Exception as e:
                log.error(f"Error crítico en ejecutar-calculo: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail={"mensaje": str(e)})

@router.get("/descargar-excel")
async def descargar_reporte_excel(request: Request):
    db_pool = get_db_pool(request)
    log.info("Generando reporte Excel unificado...")

    query = """
        SELECT 
            a.created_dt as "Fecha Creación", 
            a.order_number as "Número de Orden", 
            a.gsm as "Línea/GSM", 
            a.type as "Tipo Cliente", 
            a.operation_code as "Código Operación", 
            a.operation_type as "Nombre Operación",
            b.display_value as "Plan Origen", 
            b1.display_value as "Plan Destino",
            c.display_value as "Servicio Agregado", 
            c1.display_value as "Servicio Removido",
            a.c2p_recharge as "Monto Recarga", 
            a.executive_agent as "Agente Ejecutivo", 
            a.source_agent as "Agente Origen", 
            a.locality as "Localidad", 
            a.region as "Región",
            a.final_amount as "Monto Comisión",
            COALESCE(SUM(REPLACE(r.amount, ',', '.')::numeric), 0) AS total_recargas,
            a.period_id as "ID Periodo"
        FROM scc_user.operations_tmp a
        LEFT JOIN scc_user.plans b on (a.origin_plan = b.id_plan)
        LEFT JOIN scc_user.plans b1 on (a.destination_plan = b1.id_plan)
        LEFT JOIN scc_user.services c on (a.added_service = c.id_service)
        LEFT JOIN scc_user.services c1 on (a.removed_service = c1.id_service)
        LEFT JOIN scc_user.recharge r ON ('58'||SubStr(a.gsm,2) = r.gsm)
        WHERE a.commissionable_flag = 'Y'
        GROUP BY
            a.created_dt,
            a.order_number,
            a.gsm,
            a.type,
            a.operation_code, 
            a.operation_type, 
            b.display_value,
            b1.display_value, 
            c.display_value,
            c1.display_value, 
            a.c2p_recharge,
            a.executive_agent,
            a.source_agent,
            a.locality,
            a.region,
            a.final_amount,
            a.period_id
        ORDER BY a.created_dt DESC
    """

    try:
        async with db_pool.acquire() as conn:
            # Ejecutamos la consulta única
            rows = await conn.fetch(query, timeout=120)

        if not rows:
            log.warning("No se encontraron datos comisionables para exportar.")
            # Opcional: podrías retornar un error 404 o un excel vacío
        
        # Convertimos los registros a una lista de diccionarios
        df = pd.DataFrame([dict(row) for row in rows])

        # Creamos el buffer en memoria
        output = BytesIO()
        
        # Usamos XlsxWriter para darle un formato limpio
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Detalle Comisiones', index=False)
            
            # Ajuste automático de columnas (opcional pero recomendado)
            workbook  = writer.book
            worksheet = writer.sheets['Detalle Comisiones']
            header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})
            
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, len(str(value)) + 5)

        output.seek(0)
        log.info(f"Reporte Excel generado con {len(rows)} registros.")
        
        return StreamingResponse(
            output, 
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
            headers={"Content-Disposition": "attachment; filename=Reporte_General_Comisiones.xlsx"}
        )

    except Exception as e:
        log.error(f"Error al generar Excel unificado: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al generar el reporte")

@router.get("/lista-publicacion")
async def obtener_lista_publicacion(request: Request):
    db_pool = get_db_pool(request)
    log.debug("Consultando lista de agentes para publicación.")
    try:
        async with db_pool.acquire() as conn:
            query = """
                SELECT DISTINCT region, source_agent, locality 
                FROM scc_user.operations_tmp 
                WHERE commissionable_flag = 'Y'
                ORDER BY region;
            """
            rows = await conn.fetch(query)
            log.info(f"Lista de publicación cargada: {len(rows)} agentes encontrados.")
            return [dict(r) for r in rows]
    except Exception as e:
        log.error(f"Error en lista-publicacion: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/publicar-comisiones")
async def publicar_comisiones(request: Request, data: dict):
    db_pool = get_db_pool(request)
    agentes = data.get("agentes", [])
    period_id = data.get("period_id")
    log.info(f"Iniciando publicación para periodo {period_id}. Total agentes: {len(agentes)}")
    
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            try:
                log.debug("Ejecutando sp_operations_history...")
                await conn.execute("CALL scc_user.sp_operations_history()", timeout=300)

                if agentes:
                    log.debug(f"Actualizando flag de publicación para {len(agentes)} agentes.")
                    await conn.execute("""
                        UPDATE scc_user.operations_history 
                        SET publish_flag = 'Y' 
                        WHERE source_agent = ANY($1) AND period_id = $2
                    """, agentes, period_id)

                log.info(f"Publicación exitosa para el periodo {period_id}")
                return {"status": "EXITO", "mensaje": "Comisiones publicadas correctamente."}
            except Exception as e:
                log.error(f"Error en publicar-comisiones: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail=str(e))

# MIGRACIÓN ORACLE A POSTGRESQL 
# MIGRACIÓN OPERACIONES CRM360

@router.post("/migrar-activaciones")
async def migrar_activaciones_oracle_to_pg(
    request: Request,
    fecha_inicio: str = Body(..., example="01.02.2026"),
    fecha_fin: str = Body(..., example="28.02.2026")
):
    pg_pool = get_db_pool(request)
    log.info(f"Iniciando migración SQL360 -> PG desde {fecha_inicio} hasta {fecha_fin}")

    try:
        # 1. Conexión a Oracle SQL360 usando SETTINGS
        conn_ora = oracledb.connect(
            user=settings.ORA_SQL_USER.upper(),
            password=settings.ORA_SQL_PASS,
            dsn=settings.ORA_SQL_DSN
        )
        cursor_ora = conn_ora.cursor()

        oracle_query = """
            SELECT DISTINCT
                a.created_dt, a.id_order, b.component_value, e.id_component,
                Decode(a.id_billing,'BI-002','PREPAGO','BI-003','POSTPAGO',a.id_billing),
                a.id_order_type, t.display_value, c1.id_component, c.id_component,
                d.id_component, d1.id_component, to_char(r.amount), a.created_who,
                u.position, ul.display_value, ur.display_value     
            FROM ic_order a
            INNER JOIN ic_order_items b ON (a.id_order = b.id_order AND b.id_component = 'INV-001')
            LEFT JOIN ic_order_items c ON (a.id_order = c.id_order AND c.id_order_item_type = 'OIT-002')
            LEFT JOIN ic_order_items c1 ON (a.id_order = c1.id_order AND c1.id_order_item_type = 'OIT-008')
            LEFT JOIN ic_order_items d ON (a.id_order = d.id_order AND d.id_order_item_type = 'OIT-003')
            LEFT JOIN ic_order_items d1 ON (a.id_order = d1.id_order AND d1.id_order_item_type = 'OIT-035')
            LEFT JOIN ic_order_items e ON (a.id_order = e.id_order AND e.id_order_item_type = 'OIT-001')
            LEFT JOIN c2p_transaction r ON (a.id_order = r.id_order)
            INNER JOIN ic_order_types t ON (a.id_order_type = t.id_order_type)
            INNER JOIN ic_user u ON (Upper(a.created_who) = Upper(u.username))
            INNER JOIN ic_user_locality ul ON (u.location = ul.id_locality)
            INNER JOIN ic_user_region ur ON (u.region = ur.id_region)
            WHERE a.created_dt BETWEEN To_Date(:f1, 'dd.mm.yyyy hh24:mi:ss')
                AND TO_DATE(:f2, 'dd.mm.yyyy hh24:mi:ss')
                AND a.id_order_type IN ('OT-001','OT-016','OT-014','OT-010','OT-071','OT-015','OT-045','OT-005','OT-044','OT-030','OT-036','OT-074')
                AND a.order_status IN (0,3)
                AND u.channel IN ('AI','AA','AC') 
        """
        
        cursor_ora.execute(oracle_query, f1=f"{fecha_inicio} 00:00:00", f2=f"{fecha_fin} 23:59:59")
        rows = cursor_ora.fetchall()
        
        # 2. Transacción en PostgreSQL
        async with pg_pool.acquire() as pg_conn:
            async with pg_conn.transaction():
                await pg_conn.execute("TRUNCATE TABLE scc_user.operations")
                if rows:
                    await pg_conn.copy_records_to_table(
                        'operations', schema_name='scc_user', records=rows
                    )

        cursor_ora.close()
        conn_ora.close()
        return {"status": "EXITO", "mensaje": f"Sincronización SQL360 completada: {len(rows)} registros."}

    except Exception as e:
        log.error(f"Error en migración activaciones: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/migrar-recargas")
async def migrar_recargas_oracle_to_pg(
    request: Request,
    fecha_inicio: str = Body(..., example="01.02.2026"),
    fecha_fin: str = Body(..., example="28.02.2026")
):
    pg_pool = get_db_pool(request)
    log.info("Iniciando migración de recargas desde CRMGOLD")

    conn_crmgold = None

    try:
        # =====================================================
        # 1. Conexión a Oracle CRMGOLD
        # =====================================================
        conn_crmgold = oracledb.connect(
            user=settings.ORA_CRM_USER.upper(),
            password=settings.ORA_CRM_PASS,
            dsn=settings.ORA_CRM_DSN
        )
        cur = conn_crmgold.cursor()

        query = """
            SELECT
                TO_CHAR(reload_date, 'dd.mm.yyyy hh24:mi:ss') ||
                '{' || recharge_comment
            FROM repgold.RELOAD
            WHERE reload_date BETWEEN
                  TO_DATE(:f1, 'dd.mm.yyyy hh24:mi:ss')
              AND TO_DATE(:f2, 'dd.mm.yyyy hh24:mi:ss')
            AND recharge_comment IS NOT NULL
        """

        cur.execute(
            query,
            f1=f"{fecha_inicio} 00:00:00",
            f2=f"{fecha_fin} 23:59:59"
        )

        registros = []

        # =====================================================
        # 2. Parseo EXACTO del payload
        # =====================================================
        registros = []

        for (registro_raw,) in cur.fetchall():
            partes = registro_raw.split("{")

            if len(partes) < 8:
                # registro corrupto o incompleto
                continue
            
            try:
                created_dt = datetime.strptime(
                partes[0],
                "%d.%m.%Y %H:%M:%S"
            )
            except ValueError:
                continue
                
            registros.append((
                created_dt, # datetime
                partes[1],  # fixed_number
                partes[2],  # institution_code
                partes[3],  # channel
                partes[4],  # fixed
                partes[5],  # amount
                partes[6],  # transaction_code
                partes[7]   # gsm
            ))

        # =====================================================
        # 3. Carga en PostgreSQL
        # =====================================================
        async with pg_pool.acquire() as pg_conn:
            async with pg_conn.transaction():

                # Limpieza total
                await pg_conn.execute(
                    "TRUNCATE TABLE scc_user.recharge"
                )

                if registros:
                    await pg_conn.copy_records_to_table(
                        table_name="recharge",
                        schema_name="scc_user",
                        records=registros,
                        columns=[
                            "created_dt",
                            "fixed_number",
                            "institution_code",
                            "channel",
                            "fixed",
                            "amount",
                            "transaction_code",
                            "gsm"
                        ]
                    )

        log.info(f"Migración finalizada. Registros insertados: {len(registros)}")

        return {
            "status": "EXITO",
            "registros_insertados": len(registros)
        }

    except Exception as e:
        log.error("Error en migración de recargas", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if conn_crmgold:
            conn_crmgold.close()

