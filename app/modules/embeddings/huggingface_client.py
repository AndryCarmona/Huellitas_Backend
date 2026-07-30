import os
import time
import requests

HF_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
HF_TEXT_EMBEDDING_URL = (
    "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction"
)


def generar_embedding_texto(texto: str, max_reintentos: int = 3) -> list[float]:
    """
    Convierte un texto en su embedding (vector de 384 números) usando
    el modelo sentence-transformers/all-MiniLM-L6-v2 vía Hugging Face
    Inference API.

    Puede tardar la primera vez si el modelo está "frío" (cold start),
    en cuyo caso Hugging Face responde 503 con un tiempo estimado de
    espera. Reintentamos automáticamente en ese caso.
    """
    if not HF_API_TOKEN:
        raise RuntimeError(
            "HUGGINGFACE_API_TOKEN no está configurado en las variables de entorno."
        )

    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {"inputs": texto}

    for intento in range(max_reintentos):
        try:
            response = requests.post(
                HF_TEXT_EMBEDDING_URL, headers=headers, json=payload, timeout=30
            )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error de conexión con Hugging Face: {e}")

        if response.status_code == 200:
            embedding = response.json()

            if not isinstance(embedding, list) or not all(
                isinstance(x, (int, float)) for x in embedding
            ):
                raise RuntimeError(
                    f"Formato de embedding inesperado: {embedding}"
                )

            return embedding

        if response.status_code == 503:
            # El modelo está "cargando" en el servidor de Hugging Face (cold start)
            data = response.json()
            espera = data.get("estimated_time", 5)
            time.sleep(min(espera, 20))
            continue

        raise RuntimeError(
            f"Error de Hugging Face ({response.status_code}): {response.text}"
        )

    raise RuntimeError(
        "No se pudo generar el embedding tras varios intentos "
        "(el modelo tardó demasiado en cargar)."
    )