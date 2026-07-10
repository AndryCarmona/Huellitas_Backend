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

def obtener_estado_reporte(reporte_id: int):
    """Obtiene el estado actual del reporte."""
    return reporte_repo.obtener_estado_reporte(reporte_id)

def subir_evidencia_seguimiento(file_bytes: bytes, filename: str) -> str:
    """Sube evidencia específica del seguimiento del reporte."""
    ext = filename.split(".")[-1]
    nombre_unico = f"{uuid.uuid4()}.{ext}"

    supabase.storage.from_(BUCKET_SEGUIMIENTO).upload(
        nombre_unico,
        file_bytes,
        file_options={"content-type": f"image/{ext}"}
    ) 

    url_publica = supabase.storage.from_(BUCKET_SEGUIMIENTO).get_public_url(nombre_unico)
    return url_publica

def actualizar_estado_reporte(reporte_id: int, nueva_fase_id: int, file_bytes: bytes, filename: str, comentarios: str = None):
    """Actualiza el estado del reporte y sube la evidencia al bucket de seguimiento."""
    url_evidencia = subir_evidencia_seguimiento(file_bytes, filename)

    reporte_repo.actualizar_estado_reporte(
        reporte_id=reporte_id,
        nueva_fase_id=nueva_fase_id,
        evidencia_url=url_evidencia,
        usuario_id=usuario_id,
        comentarios=comentarios
    )

    return {
        "message": "Estado actualizado correctamente",
        "nueva_fase_id": nueva_fase_id,
        "evidencia_url": url_evidencia
    }