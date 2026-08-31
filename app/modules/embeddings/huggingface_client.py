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

#ADOPCIONES - EVALUACIÓN DE RESPUESTAS
def evaluar_respuesta_adopcion(
    pregunta: str,
    criterio_esperado: str,
    respuesta: str,
    max_reintentos: int = 3,
) -> tuple[float, str]:
    """
    Usa un LLM instruction-tuned como juez para calificar (0-100) qué tan
    bien una respuesta de un postulante cumple lo que el dueño busca,
    devolviendo (score, justificacion_breve).
    """
    if not HF_API_TOKEN:
        raise RuntimeError(
            "HUGGINGFACE_API_TOKEN no está configurado en las variables de entorno."
        )

    url = "https://router.huggingface.co/v1/chat/completions"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

    prompt = (
        "Eres un evaluador imparcial para un proceso de adopción de mascotas.\n"
        f"Pregunta hecha al postulante: {pregunta}\n"
        f"Lo que el dueño de la mascota busca en la respuesta: {criterio_esperado}\n"
        f"Respuesta del postulante: {respuesta}\n\n"
        "Califica de 0 a 100 qué tan bien la respuesta cumple lo que el dueño "
        "busca. Responde ÚNICAMENTE en formato JSON así: "
        '{"score": <numero>, "justificacion": "<una oración breve>"}'
    )

    payload = {
        "model": "meta-llama/Llama-3.1-8B-Instruct:fastest",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 150,
    }

    for intento in range(max_reintentos):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error de conexión con Hugging Face: {e}")

        if response.status_code == 200:
            contenido = response.json()["choices"][0]["message"]["content"]
            import json
            try:
                resultado = json.loads(contenido)
                return float(resultado["score"]), resultado.get("justificacion", "")
            except (json.JSONDecodeError, KeyError):
                raise RuntimeError(f"Respuesta del LLM no es JSON válido: {contenido}")

        if response.status_code == 503:
            data = response.json()
            espera = data.get("estimated_time", 5)
            time.sleep(min(espera, 20))
            continue

        raise RuntimeError(f"Error de Hugging Face ({response.status_code}): {response.text}")

    raise RuntimeError("No se pudo evaluar la respuesta tras varios intentos.")

def generar_preguntas_sugeridas(
    especie: str,
    edad: str,
    tamano: str,
    descripcion: str | None,
    max_reintentos: int = 3,
) -> list[str]:
    """
    Sugiere preguntas de entrevista para un postulante, basadas en el
    perfil del animal en adopción.
    """
    if not HF_API_TOKEN:
        raise RuntimeError(
            "HUGGINGFACE_API_TOKEN no está configurado en las variables de entorno."
        )

    url = "https://router.huggingface.co/v1/chat/completions"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

    prompt = (
        "Eres un asistente que ayuda a dueños de mascotas a preparar preguntas "
        "para entrevistar a posibles adoptantes.\n"
        f"Animal: {especie}, edad {edad}, tamaño {tamano}.\n"
        f"Descripción adicional: {descripcion or 'ninguna'}\n\n"
        "Sugiere 5 preguntas relevantes para evaluar si un postulante es "
        "buen candidato para adoptar a este animal. Responde ÚNICAMENTE en "
        'formato JSON así: {"preguntas": ["pregunta 1", "pregunta 2", ...]}'
    )

    payload = {
        "model": "meta-llama/Llama-3.1-8B-Instruct:fastest",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 400,
    }

    for intento in range(max_reintentos):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error de conexión con Hugging Face: {e}")

        if response.status_code == 200:
            contenido = response.json()["choices"][0]["message"]["content"]
            import json
            try:
                resultado = json.loads(contenido)
                return resultado["preguntas"]
            except (json.JSONDecodeError, KeyError):
                raise RuntimeError(f"Respuesta del LLM no es JSON válido: {contenido}")

        if response.status_code == 503:
            data = response.json()
            espera = data.get("estimated_time", 5)
            time.sleep(min(espera, 20))
            continue

        raise RuntimeError(f"Error de Hugging Face ({response.status_code}): {response.text}")

    raise RuntimeError("No se pudieron generar preguntas tras varios intentos.")