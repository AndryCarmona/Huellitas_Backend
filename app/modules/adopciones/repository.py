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