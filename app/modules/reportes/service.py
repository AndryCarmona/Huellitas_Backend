from app.core.database import supabase
from .schemas import ReporteCreate
from .repository import ReporteRepository
from app.modules.insignias.repository import InsigniaRepository  
import uuid

BUCKET_NAME="evidencia_reporte"

# Instancias de los repositorios
reporte_repo = ReporteRepository()
insignia_repo = InsigniaRepository()

# Umbrales de insignias por nivel (ajusta según tu lógica de negocio)
UMBRAL_NIVEL = {
    1: 1,    # Nivel 1: 3 reportes
    2: 3,   # Nivel 2: 10 reportes
    3: 5,   # Nivel 3: 25 reportes
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

def listar_reportes():
    response = supabase.table("reporte").select("*").execute()
    return response.data

#CONTAR NUMERO DE REPORTES PARA ASIGNARLE LA INSIGNIAAAAA
def _verificar_insignias_reportes(usuario_id: int):
    total_reportes = reporte_repo.contar_reportes_usuario(usuario_id)
    print(f"Usuario {usuario_id} tiene {total_reportes} reportes")

    insignias_reporte = insignia_repo.obtener_insignias_por_categoria("reporte")
    insignias_ya_obtenidas = insignia_repo.obtener_insignias_de_usuario(usuario_id)
    
    ids_ya_obtenidas = {ins["insignias_id"] for ins in insignias_ya_obtenidas}

    for insignia in insignias_reporte:
        insignia_id = insignia["id_insignias"]
        nivel = insignia["nivel"]

        if insignia_id in ids_ya_obtenidas:
            continue

        umbral = UMBRAL_NIVEL.get(nivel, 999)
        if total_reportes >= umbral:
            insignia_repo.otorgar_insignia(usuario_id, insignia_id)
            print(f"¡Usuario {usuario_id} obtuvo la insignia: {insignia['nombre']}!")