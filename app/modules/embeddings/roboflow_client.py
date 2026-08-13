import os
from inference_sdk import InferenceHTTPClient

ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")

_client = InferenceHTTPClient(
    api_url="https://infer.roboflow.com",
    api_key=ROBOFLOW_API_KEY,
)


def generar_embedding_imagen(imagen_url: str) -> list[float]:
    """
    Convierte una imagen (dada su URL pública) en un embedding de 512
    números usando CLIP, vía el servicio hospedado de Roboflow.
    """
    if not ROBOFLOW_API_KEY:
        raise RuntimeError("ROBOFLOW_API_KEY no está configurado en las variables de entorno")

    try:
        resultado = _client.get_clip_image_embeddings(inference_input=imagen_url)
    except Exception as e:
        raise RuntimeError(f"Error al generar embedding de imagen: {e}")

    embeddings = resultado.get("embeddings")
    if not embeddings or not isinstance(embeddings, list):
        raise RuntimeError(f"Formato de respuesta inesperado de Roboflow: {resultado}")

    return embeddings[0]