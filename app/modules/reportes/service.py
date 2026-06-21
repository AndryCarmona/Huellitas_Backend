from app.core.database import supabase
from .schemas import ReporteCreate
import uuid

BUCKET_NAME="evidencia_reporte"

def crear_reporte(data: ReporteCreate):
    payload = data.dict()
    payload["fecha_reporte"] = "now()"

    response = supabase.table("reporte").insert(payload).execute()
    return response.data

def subir_evidencia(file_bytes: bytes, filename: str) -> str:
    ext = filename.split(".")[-1]
    nombre_unico = f"{uuid.uuid4()}.{ext}"

    supabase.storage.from_(BUCKET_NAME).upload(
        nombre_unico,
        file_bytes,
        file_options={"content-type": f"image/{ext}"}
    ) 

    url_publica = supabase.storage.from_(BUCKET_NAME).get_public_url(nombre_unico)
    return url_publica