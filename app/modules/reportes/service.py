from app.core.database import supabase
from .schemas import ReporteCreate
from .repository import ReporteRepository
from app.modules.insignias.repository import InsigniaRepository  
import uuid

BUCKET_NAME="evidencia_reporte"
BUCKET_SEGUIMIENTO = "evidencia_seguimiento" 

# Instancias de los repositorios
reporte_repo = ReporteRepository()
insignia_repo = InsigniaRepository()

# Umbrales de insignias por nivel
UMBRAL_NIVEL = {
    1: 1,    # Nivel 1: 1 reportes
    2: 3,   # Nivel 2: 3 reportes
    3: 5,   # Nivel 3: 5 reportes
    4: 10,
    5: 25,
    6: 50,
    7: 100  
}

def crear_reporte(data: ReporteCreate):
    payload = data.dict()
    payload["fecha_reporte"] = "now()"
    print("PAYLOAD A INSERTAR:", payload)

    response = supabase.table("reporte").insert(payload).execute()
    
    _verificar_insignias_reportes(data.usuario_id_fk)

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
