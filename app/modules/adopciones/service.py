from app.core.database import supabase
from app.modules.embeddings.huggingface_client import (
    generar_preguntas_sugeridas,
    evaluar_respuesta_adopcion,
)
from .schemas import AdopcionCreate, PostulacionCreate, SugerirPreguntasRequest


def _adopcion_con_preguntas(adopcion_id: int) -> dict:
    adopcion = (
        supabase.table("adopcion")
        .select("*")
        .eq("adopcion_id", adopcion_id)
        .single()
        .execute()
        .data
    )
    if not adopcion:
        raise ValueError("No se encontró la adopción.")

    preguntas = (
        supabase.table("adopcion_pregunta")
        .select("*")
        .eq("adopcion_id_fk", adopcion_id)
        .order("orden")
        .execute()
        .data
    )
    adopcion["preguntas"] = preguntas
    return adopcion


def crear_adopcion(data: AdopcionCreate) -> dict:
    adopcion_row = data.model_dump(exclude={"preguntas"})
    adopcion = supabase.table("adopcion").insert(adopcion_row).execute().data[0]

    preguntas_creadas = []
    for i, pregunta in enumerate(data.preguntas):
        fila = {
            "adopcion_id_fk": adopcion["adopcion_id"],
            "texto": pregunta.texto,
            "criterio_esperado": pregunta.criterio_esperado,
            "orden": i,
        }
        preguntas_creadas.append(
            supabase.table("adopcion_pregunta").insert(fila).execute().data[0]
        )

    adopcion["preguntas"] = preguntas_creadas
    return adopcion


def listar_adopciones() -> list[dict]:
    adopciones = (
        supabase.table("adopcion")
        .select("*")
        .eq("estado", "activa")
        .order("fecha_adopcion", desc=True)
        .execute()
        .data
    )
    for adopcion in adopciones:
        preguntas = (
            supabase.table("adopcion_pregunta")
            .select("*")
            .eq("adopcion_id_fk", adopcion["adopcion_id"])
            .order("orden")
            .execute()
            .data
        )
        adopcion["preguntas"] = preguntas
    return adopciones


def obtener_adopcion(adopcion_id: int) -> dict:
    return _adopcion_con_preguntas(adopcion_id)


def eliminar_adopcion(adopcion_id: int, usuario_id: int) -> None:
    adopcion = (
        supabase.table("adopcion")
        .select("usuario_id_fk")
        .eq("adopcion_id", adopcion_id)
        .single()
        .execute()
        .data
    )
    if not adopcion:
        raise ValueError("No se encontró la adopción.")
    if adopcion["usuario_id_fk"] != usuario_id:
        raise PermissionError("No puedes eliminar una adopción que no es tuya.")

    supabase.table("adopcion").delete().eq("adopcion_id", adopcion_id).execute()


def sugerir_preguntas(data: SugerirPreguntasRequest) -> list[str]:
    return generar_preguntas_sugeridas(
        especie=data.especie,
        edad=data.edad,
        tamano=data.tamano,
        descripcion=data.descripcion,
    )


def crear_postulacion(adopcion_id: int, data: PostulacionCreate) -> dict:
    adopcion = (
        supabase.table("adopcion")
        .select("adopcion_id")
        .eq("adopcion_id", adopcion_id)
        .single()
        .execute()
        .data
    )
    if not adopcion:
        raise ValueError("No se encontró la adopción.")

    postulacion_row = {
        "adopcion_id_fk": adopcion_id,
        "usuario_id_fk": data.usuario_id_fk,
    }
    postulacion = (
        supabase.table("adopcion_postulacion").insert(postulacion_row).execute().data[0]
    )

    respuestas_creadas = []
    for respuesta in data.respuestas:
        fila = {
            "postulacion_id_fk": postulacion["postulacion_id"],
            "pregunta_id_fk": respuesta.pregunta_id,
            "respuesta_texto": respuesta.respuesta_texto,
        }
        creada = supabase.table("adopcion_respuesta").insert(fila).execute().data[0]
        respuestas_creadas.append(_respuesta_a_schema(creada))

    postulacion["respuestas"] = respuestas_creadas
    return postulacion


def _verificar_dueno(adopcion_id: int, usuario_id: int) -> None:
    adopcion = (
        supabase.table("adopcion")
        .select("usuario_id_fk")
        .eq("adopcion_id", adopcion_id)
        .single()
        .execute()
        .data
    )
    if not adopcion:
        raise ValueError("No se encontró la adopción.")
    if adopcion["usuario_id_fk"] != usuario_id:
        raise PermissionError("Solo el dueño de la publicación puede ver esto.")


def listar_postulaciones(adopcion_id: int, usuario_id: int) -> list[dict]:
    _verificar_dueno(adopcion_id, usuario_id)

    postulaciones = (
        supabase.table("adopcion_postulacion")
        .select("*")
        .eq("adopcion_id_fk", adopcion_id)
        .execute()
        .data
    )
    for postulacion in postulaciones:
        respuestas = (
            supabase.table("adopcion_respuesta")
            .select("*")
            .eq("postulacion_id_fk", postulacion["postulacion_id"])
            .execute()
            .data
        )
        postulacion["respuestas"] = [_respuesta_a_schema(r) for r in respuestas]
    return postulaciones


def calcular_ranking(adopcion_id: int, usuario_id: int) -> list[dict]:
    _verificar_dueno(adopcion_id, usuario_id)

    postulaciones = listar_postulaciones(adopcion_id, usuario_id)
    preguntas = {
        p["pregunta_id"]: p
        for p in supabase.table("adopcion_pregunta")
        .select("*")
        .eq("adopcion_id_fk", adopcion_id)
        .execute()
        .data
    }

    for postulacion in postulaciones:
        scores_respuestas = []
        for respuesta in postulacion["respuestas"]:
            if respuesta["score_ia"] is None:
                pregunta = preguntas[respuesta["pregunta_id"]]
                score, justificacion = evaluar_respuesta_adopcion(
                    pregunta=pregunta["texto"],
                    criterio_esperado=pregunta["criterio_esperado"] or "Sin criterio específico",
                    respuesta=respuesta["respuesta_texto"],
                )
                supabase.table("adopcion_respuesta").update(
                    {"score_ia": score, "justificacion_ia": justificacion}
                ).eq("respuesta_id", respuesta["respuesta_id"]).execute()
                respuesta["score_ia"] = score
            scores_respuestas.append(respuesta["score_ia"])

        score_respuestas_ia = (
            sum(scores_respuestas) / len(scores_respuestas) if scores_respuestas else 0
        )

        # TODO: score_insignias pendiente de integrar con InsigniaRepository/Service
        score_insignias = 0

        score_final = 0.65 * score_respuestas_ia + 0.35 * score_insignias

        supabase.table("adopcion_postulacion").update(
            {
                "score_respuestas_ia": score_respuestas_ia,
                "score_insignias": score_insignias,
                "score_final": score_final,
            }
        ).eq("postulacion_id", postulacion["postulacion_id"]).execute()

        postulacion["score_respuestas_ia"] = score_respuestas_ia
        postulacion["score_insignias"] = score_insignias
        postulacion["score_final"] = score_final

    return sorted(postulaciones, key=lambda p: p["score_final"], reverse=True)

def _respuesta_a_schema(fila: dict) -> dict:
    return {
        "respuesta_id": fila["respuesta_id"],
        "pregunta_id": fila["pregunta_id_fk"],
        "respuesta_texto": fila["respuesta_texto"],
        "score_ia": fila.get("score_ia"),
        "justificacion_ia": fila.get("justificacion_ia"),
    }