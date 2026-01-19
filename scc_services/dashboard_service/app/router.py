from fastapi import APIRouter, HTTPException, Request
from datetime import datetime 

router = APIRouter()

@router.get("/estadisticas")
async def obtener_estadisticas(
    request: Request, 
    tipo: str = "ventas", 
    inicio: str = None, 
    fin: str = None
):
    db_pool = request.app.state.db_pool
    
    try:
        # 1. Convertir strings a objetos date de Python
        # Esto evita el error 'str object has no attribute toordinal'
        try:
            fecha_inicio_obj = datetime.strptime(inicio, "%Y-%m-%d").date() if inicio else datetime.now().date().replace(month=1, day=1)
            fecha_fin_obj = datetime.strptime(fin, "%Y-%m-%d").date() if fin else datetime.now().date()
        except ValueError:
            raise HTTPException(status_code=400, detail={"mensaje": "Formato de fecha inválido. Use YYYY-MM-DD"})

        # 2. Selección de tabla
        tabla = "scc_user.te_ventas" if tipo == "ventas" else "scc_user.te_postventa"
        
        # 3. Query (venta_creada es la columna correcta según tus tablas)
        sql_query = f"""
            SELECT 
                TO_CHAR(venta_creada, 'TMMON') AS mes_nombre,
                EXTRACT(MONTH FROM venta_creada) AS mes_num,
                COUNT(*) AS total
            FROM {tabla}
            WHERE venta_creada::date BETWEEN $1 AND $2
            GROUP BY mes_nombre, mes_num
            ORDER BY mes_num;
        """
        
        async with db_pool.acquire() as conn:
            # Enviamos los objetos de fecha, no los strings
            datos = await conn.fetch(sql_query, fecha_inicio_obj, fecha_fin_obj)
            return [dict(d) for d in datos]
            
    except Exception as e:
        print(f"DEBUG Error Dashboard: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail={"mensaje": f"Error en {tipo}: {str(e)}"}
        )