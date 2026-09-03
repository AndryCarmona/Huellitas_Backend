from uuid import uuid4
from app.core.database import supabase

BUCKET = "adopciones"


def subir_imagen_adopcion(contenido: bytes, nombre_original: str, content_type: str) -> str:
    extension = nombre_original.split(".")[-1] if "." in nombre_original else "jpg"
    ruta = f"{uuid4()}.{extension}"

    supabase.storage.from_(BUCKET).upload(
        ruta,
        contenido,
        {"content-type": content_type, "upsert": "true"},
    )

    return supabase.storage.from_(BUCKET).get_public_url(ruta)


def actualizar_imagen_adopcion(adopcion_id: int, imagen_url: str) -> dict:
    resultado = (
        supabase.table("adopcion")
        .update({"imagen_url": imagen_url})
        .eq("adopcion_id", adopcion_id)
        .execute()
        .data
    )
    if not resultado:
        raise ValueError("No se encontró la adopción.")
    return resultado[0]


def aprobar_postulacion_atomica(
    adopcion_id: int,
    postulacion_id: int,
    responsable_id: int,
    contacto_responsable: str,
) -> dict:
    """Delega la seleccion completa a PostgreSQL para obtener atomicidad real."""
    resultado = supabase.rpc(
        "aprobar_postulacion_adopcion",
        {
            "p_adopcion_id": adopcion_id,
            "p_postulacion_id": postulacion_id,
            "p_responsable_id": responsable_id,
            "p_contacto_responsable": contacto_responsable,
        },
    ).execute().data
    if isinstance(resultado, list):
        return resultado[0] if resultado else {}
    return resultado or {}
