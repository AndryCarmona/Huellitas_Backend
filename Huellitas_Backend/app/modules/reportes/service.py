from app.core.database import supabase
from .schemas import ReporteCreate

def crear_reporte(data: ReporteCreate):
    payload = data.dict()
    payload["fecha_reporte"] = "now()"

    response = supabase.table("reporte").insert(payload).execute()
    return response.data