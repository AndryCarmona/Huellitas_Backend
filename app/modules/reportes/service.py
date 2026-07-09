from app.core.database import supabase
from .schemas import ReporteCreate
import uuid

BUCKET_NAME="evidencia_reporte"

def crear_reporte(data: ReporteCreate):
    payload = data.dict()
    payload["fecha_reporte"] = "now()"
    print("PAYLOAD A INSERTAR:", payload)

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

def listar_reportes(usuario_verificado: bool = False):
    response = supabase.table("reporte").select("*").execute()
    reportes = response.data

    if not usuario_verificado:
        # tipo_reporte == 4 corresponde a "Maltrato animal"
        reportes = [r for r in reportes if r.get("tipo_reporte") != 4]

    return reportes