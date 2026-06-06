from fastapi import APIRouter, HTTPException, Request
from datetime import datetime
# --- IMPORTACIÓN DEL CONFIGURADOR DE LOGS ---
from api_gateway.utils.logger_config import setup_logger

# Inicialización del logger para el Dashboard
log = setup_logger("DASHBOARD-SERVICE")

router = APIRouter()

@router.get("/metrics")
async def obtener_metricas_dashboard(request: Request, periodo: str):
    db_pool = request.app.state.db_pool
    
    # DEBUG: Capturamos el periodo que solicita el usuario
    log.debug(f"Solicitud de métricas recibida. Periodo: {periodo}")
    
    queries = {
        "operaciones_dia": """
            SELECT 
                to_char(created_dt, 'dd.mm.yyyy') as etiqueta,
                COUNT(*) as total
            FROM scc_user.operations_history
            WHERE created_dt::text LIKE $1 || '%'
            GROUP BY to_char(created_dt, 'dd.mm.yyyy')
            ORDER BY etiqueta ASC;
        """,
        "tecnologia": """
            SELECT type as etiqueta, COUNT(*) as total
            FROM scc_user.operations_history
            WHERE to_char(created_dt, 'YYYY-MM') = $1
            GROUP BY type;
        """,
        "comisionables": """
            SELECT operation_type as etiqueta, COUNT(*) as total
            FROM scc_user.operations_history 
            WHERE to_char(created_dt, 'YYYY-MM') = $1
            GROUP BY operation_type
            ORDER BY total DESC;
        """
    }

    results = {}
    try:
        async with db_pool.acquire() as conn:
            for key, sql in queries.items():
                # DEBUG: Trazabilidad de ejecución de cada métrica
                log.debug(f"Ejecutando consulta analítica: {key}")
                data = await conn.fetch(sql, periodo)
                results[key] = [dict(d) for d in data]
        
        # INFO: Confirmación de carga exitosa
        log.info(f"Métricas generadas correctamente para el periodo {periodo}")
        return results

    except Exception as e:
        # ERROR: Reemplazamos el print por log.error con rastro completo
        log.error(f"Error crítico al procesar métricas del Dashboard (Periodo: {periodo}): {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno al procesar métricas")