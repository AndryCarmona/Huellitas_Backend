from app.core.database import supabase
from .schemas import ReporteCreate
from .repository import ReporteRepository
from app.modules.insignias.repository import InsigniaRepository  
from app.modules.embeddings.huggingface_client import generar_embedding_texto
from app.modules.embeddings.roboflow_client import generar_embedding_imagen
from app.modules.embeddings.faiss_index import faiss_service
from app.modules.embeddings.faiss_index_imagen import faiss_imagen_service

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

TIPO_ANIMAL_LABELS = {1: "perro", 2: "gato"}

def _construir_texto_embedding(data: ReporteCreate) -> str:
    """El embedding se genera únicamente de la descripción libre.
    Tipo de animal ya se filtra de forma dura por separado; raza y
    tamaño se excluyen porque distorsionan la similitud semántica
    (dos reportes del mismo animal casi nunca coinciden en la raza
    percibida por el usuario)."""
    return data.descripcion

def crear_reporte(data: ReporteCreate, forzar_creacion: bool = False):
    texto_embedding = _construir_texto_embedding(data)
    embedding_texto = generar_embedding_texto(texto_embedding)
    embedding_imagen = generar_embedding_imagen(data.evidencia)

    if not forzar_creacion:
        candidatos_texto = faiss_service.buscar_similares(
            embedding=embedding_texto,
            latitud=data.latitud,
            longitud=data.longitud,
            tipo_animal=data.tipo_animal,
        )
        candidatos_imagen = faiss_imagen_service.buscar_similares(
            embedding=embedding_imagen,
            latitud=data.latitud,
            longitud=data.longitud,
            tipo_animal=data.tipo_animal,
        )

        candidatos_combinados = _combinar_candidatos(candidatos_texto, candidatos_imagen)

        if candidatos_combinados:
            detalles = _obtener_detalles_candidatos(
                [c["reporte_id"] for c in candidatos_combinados]
            )
            for c in candidatos_combinados:
                c["detalle"] = detalles.get(c["reporte_id"])

            return {
                "posible_duplicado": True,
                "candidatos": candidatos_combinados,
                "reporte": None,
            }

    payload = data.dict()
    payload["fecha_reporte"] = "now()"
    payload["embedding_texto"] = embedding_texto
    payload["embedding_imagen"] = embedding_imagen

    response = supabase.table("reporte").insert(payload).execute()
    reporte_creado = response.data[0]

    faiss_service.agregar(
        reporte_id=reporte_creado["reporte_id"],
        embedding=embedding_texto,
        latitud=data.latitud,
        longitud=data.longitud,
        fecha_reporte=reporte_creado["fecha_reporte"],
        tipo_animal=data.tipo_animal,
    )
    faiss_imagen_service.agregar(
        reporte_id=reporte_creado["reporte_id"],
        embedding=embedding_imagen,
        latitud=data.latitud,
        longitud=data.longitud,
        fecha_reporte=reporte_creado["fecha_reporte"],
        tipo_animal=data.tipo_animal,
    )

    _verificar_insignias_reportes(data.usuario_id_fk)

    return {
        "posible_duplicado": False,
        "candidatos": None,
        "reporte": reporte_creado,
    }

def _combinar_candidatos(candidatos_texto: list[dict], candidatos_imagen: list[dict]) -> list[dict]:
    """Une los candidatos de ambas búsquedas por reporte_id. Si un mismo
    reporte aparece en ambas listas, se queda con el score más alto y se
    guardan ambos scores para referencia."""
    combinados: dict[int, dict] = {}

    for c in candidatos_texto:
        combinados[c["reporte_id"]] = {
            "reporte_id": c["reporte_id"],
            "score_texto": c["score"],
            "score_imagen": None,
            "distancia_km": c["distancia_km"],
        }

    for c in candidatos_imagen:
        if c["reporte_id"] in combinados:
            combinados[c["reporte_id"]]["score_imagen"] = c["score"]
        else:
            combinados[c["reporte_id"]] = {
                "reporte_id": c["reporte_id"],
                "score_texto": None,
                "score_imagen": c["score"],
                "distancia_km": c["distancia_km"],
            }

    resultado = list(combinados.values())
    resultado.sort(
        key=lambda c: max(c["score_texto"] or 0, c["score_imagen"] or 0),
        reverse=True,
    )
    return resultado

def _obtener_detalles_candidatos(reporte_ids: list[int]) -> dict[int, dict]:
    response = (
        supabase.table("reporte")
        .select("reporte_id, descripcion, evidencia, tipo_animal, tamano")
        .in_("reporte_id", reporte_ids)
        .execute()
    )
    return {r["reporte_id"]: r for r in response.data}


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

    # Trae todo el historial de fases, ordenado del más reciente al más antiguo
    historial_response = (
        supabase.table("historial_fases_reporte")
        .select("reporte_id, fase_id, fecha_cambio")
        .order("fecha_cambio", desc=True)
        .execute()
    )
    historial = historial_response.data

    ultima_fase_por_reporte = {}
    ultima_fecha_por_reporte = {}
    for h in historial:
        rid = h["reporte_id"]
        if rid not in ultima_fecha_por_reporte:
            ultima_fecha_por_reporte[rid] = h["fecha_cambio"]
            ultima_fase_por_reporte[rid] = h["fase_id"]

    for r in reportes:
        rid = r.get("reporte_id")
        r["fecha_actualizacion"] = ultima_fecha_por_reporte.get(rid)
        r["fase_actual"] = ultima_fase_por_reporte.get(rid)

    return reportes

#CONTAR NUMERO DE REPORTES PARA ASIGNARLE LA INSIGNIAAAAA
def _verificar_insignias_reportes(usuario_id: int):
    total_reportes = reporte_repo.contar_reportes_usuario(usuario_id)
    print(f"Usuario {usuario_id} tiene {total_reportes} reportes")

    insignias_reporte = insignia_repo.obtener_insignias_por_categoria("reporte")
    insignias_ya_obtenidas = insignia_repo.obtener_insignias_de_usuario(usuario_id)
    
    ids_ya_obtenidas = {ins["insignia_id"] for ins in insignias_ya_obtenidas}

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

def actualizar_estado_reporte(reporte_id: int, nueva_fase_id: int, file_bytes: bytes, filename: str, usuario_id: int = None, comentarios: str = None):
    """Actualiza el estado del reporte y sube la evidencia al bucket de seguimiento."""
    url_evidencia = subir_evidencia_seguimiento(file_bytes, filename)

    reporte_repo.actualizar_estado_reporte(
        reporte_id=reporte_id,
        nueva_fase_id=nueva_fase_id,
        evidencia_url=url_evidencia,
        usuario_id=usuario_id,
        comentarios=comentarios
    )

    if nueva_fase_id == 3 and usuario_id is not None:
        _verificar_insignia_rescate(usuario_id)

    return {
        "message": "Estado actualizado correctamente",
        "nueva_fase_id": nueva_fase_id,
        "evidencia_url": url_evidencia
    }

#Insignias para rescates
def _verificar_insignia_rescate(usuario_id: int):
    """Cuenta cuántos reportes completo el usuario y otorga insignias."""
    
    response = (
        supabase.table("historial_fases_reporte")
        .select("id_historial_fases", count="exact")
        .eq("fase_id", 3) 
        .eq("usuario_id", usuario_id)
        .execute()
    )
    
    total_rescates = response.count or 0
    print(f"Usuario {usuario_id} tiene {total_rescates} rescates")

    insignias_categoria = insignia_repo.obtener_insignias_por_categoria("rescate")
    insignias_ya_obtenidas = insignia_repo.obtener_insignias_de_usuario(usuario_id)
    
    ids_ya_obtenidas = {ins["insignia_id"] for ins in insignias_ya_obtenidas}

    for insignia in insignias_categoria:
        insignia_id = insignia["id_insignias"]
        nivel = insignia["nivel"]

        if insignia_id in ids_ya_obtenidas:
            continue

        umbral = UMBRAL_NIVEL.get(nivel, 999)
        if total_rescates >= umbral:
            insignia_repo.otorgar_insignia(usuario_id, insignia_id)
            print(f"Usuario {usuario_id} obtuvo la insignia: {insignia['nombre']}")

def tomar_reporte(reporte_id: int, usuario_id: int):
    """Asigna al usuario actual como responsable del rescate."""
    return reporte_repo.tomar_reporte(reporte_id, usuario_id)
