from app.core.database import supabase
from app.modules.embeddings.huggingface_client import (
    generar_preguntas_sugeridas,
    evaluar_respuesta_adopcion,
)
from .schemas import AdopcionCreate, PostulacionCreate, SugerirPreguntasRequest
from fastapi import UploadFile
from .repository import (
    subir_imagen_adopcion,
    actualizar_imagen_adopcion,
    aprobar_postulacion_atomica,
)
from app.modules.insignias.repository import InsigniaRepository

def subir_imagen(adopcion_id: int, archivo: UploadFile, usuario_id: int) -> dict:
    _verificar_dueno(adopcion_id, usuario_id)
    contenido = archivo.file.read()
    url = subir_imagen_adopcion(contenido, archivo.filename, archivo.content_type)
    return actualizar_imagen_adopcion(adopcion_id, url)

def _ocultar_contactos_adopcion(adopcion: dict) -> dict:
    adopcion.pop("contacto_responsable", None)
    adopcion.pop("contacto_adoptante", None)
    return adopcion


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
    return _ocultar_contactos_adopcion(adopcion)


def crear_adopcion(data: AdopcionCreate, usuario_id: int) -> dict:
    adopcion_row = data.model_dump(exclude={"preguntas"})
    adopcion_row["usuario_id_fk"] = usuario_id
    adopcion_row["estado"] = "activa"
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
        _ocultar_contactos_adopcion(adopcion)
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


def _es_pregunta_contacto(pregunta: dict) -> bool:
    return "medio de contacto" in (pregunta.get("texto") or "").strip().lower()


def crear_postulacion(adopcion_id: int, data: PostulacionCreate, usuario_id: int) -> dict:
    adopcion = (
        supabase.table("adopcion")
        .select("adopcion_id,usuario_id_fk,estado")
        .eq("adopcion_id", adopcion_id)
        .single()
        .execute()
        .data
    )
    if not adopcion:
        raise ValueError("No se encontró la adopción.")
    if adopcion.get("estado") != "activa":
        raise ValueError("Esta adopción ya no recibe postulaciones.")
    if adopcion.get("usuario_id_fk") == usuario_id:
        raise ValueError("No puedes postularte a tu propia adopción.")

    preguntas = {
        p["pregunta_id"]: p
        for p in supabase.table("adopcion_pregunta")
        .select("pregunta_id,texto")
        .eq("adopcion_id_fk", adopcion_id)
        .execute()
        .data
    }
    ids_respuestas = [r.pregunta_id for r in data.respuestas]
    if len(ids_respuestas) != len(set(ids_respuestas)):
        raise ValueError("No se puede responder dos veces la misma pregunta.")
    if set(ids_respuestas) != set(preguntas):
        raise ValueError("Debes responder exactamente las preguntas de esta adopción.")

    contacto = next(
        (
            r.respuesta_texto.strip()
            for r in data.respuestas
            if _es_pregunta_contacto(preguntas[r.pregunta_id])
        ),
        None,
    )
    if not contacto:
        raise ValueError("Debes proporcionar un medio de contacto.")

    postulacion_row = {
        "adopcion_id_fk": adopcion_id,
        "usuario_id_fk": usuario_id,
        "estado": "pendiente",
        "contacto": contacto,
    }
    postulacion = (
        supabase.table("adopcion_postulacion").insert(postulacion_row).execute().data[0]
    )

    respuestas_creadas = []
    for respuesta in data.respuestas:
        if _es_pregunta_contacto(preguntas[respuesta.pregunta_id]):
            continue
        fila = {
            "postulacion_id_fk": postulacion["postulacion_id"],
            "pregunta_id_fk": respuesta.pregunta_id,
            "respuesta_texto": respuesta.respuesta_texto,
        }
        creada = supabase.table("adopcion_respuesta").insert(fila).execute().data[0]
        respuestas_creadas.append(_respuesta_a_schema(creada))

    postulacion["respuestas"] = respuestas_creadas
    postulacion.pop("contacto", None)
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

    adopcion = (
        supabase.table("adopcion")
        .select("estado,adoptante_id")
        .eq("adopcion_id", adopcion_id)
        .single()
        .execute()
        .data
    )
    preguntas_por_id = {
        pregunta["pregunta_id"]: pregunta
        for pregunta in supabase.table("adopcion_pregunta")
        .select("pregunta_id,texto")
        .eq("adopcion_id_fk", adopcion_id)
        .execute()
        .data
    }

    postulaciones = (
        supabase.table("adopcion_postulacion")
        .select("*")
        .eq("adopcion_id_fk", adopcion_id)
        .execute()
        .data
    )
    for postulacion in postulaciones:
        seleccionada = (
            adopcion.get("estado") == "completada"
            and postulacion.get("estado") == "aceptada"
            and postulacion.get("usuario_id_fk") == adopcion.get("adoptante_id")
        )
        postulacion["contacto"] = postulacion.get("contacto") if seleccionada else None
        postulacion["fue_aceptada"] = seleccionada
        respuestas = (
            supabase.table("adopcion_respuesta")
            .select("*")
            .eq("postulacion_id_fk", postulacion["postulacion_id"])
            .execute()
            .data
        )
        postulacion["respuestas"] = [
            _respuesta_a_schema(r)
            for r in respuestas
            if not _es_pregunta_contacto(
                preguntas_por_id.get(r["pregunta_id_fk"], {})
            )
        ]

        usuario = (
            supabase.table("usuario")
            .select("nombre_usuario, foto_perfil, ciudad, estado, fecha_registro_usuario")
            .eq("usuario_id_pk", postulacion["usuario_id_fk"])
            .single()
            .execute()
            .data
        )
        conteo = _conteo_insignias_por_categoria(postulacion["usuario_id_fk"])

        postulacion["nombre_usuario"] = usuario.get("nombre_usuario") if usuario else None
        postulacion["foto_perfil"] = usuario.get("foto_perfil") if usuario else None
        postulacion["ciudad"] = usuario.get("ciudad") if usuario else None
        postulacion["estado_usuario"] = usuario.get("estado") if usuario else None
        postulacion["fecha_registro_usuario"] = usuario.get("fecha_registro_usuario") if usuario else None
        postulacion["insignias_rescate"] = conteo["rescate"]
        postulacion["insignias_reporte"] = conteo["reporte"]
        postulacion["insignias_donacion"] = conteo["donacion"]
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

        score_insignias = _calcular_score_insignias(postulacion["usuario_id_fk"])

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

def _calcular_score_insignias(usuario_id: int) -> float:
    repo = InsigniaRepository()
    catalogo = repo.obtener_catalogo_insignias()
    obtenidas = repo.obtener_insignias_de_usuario(usuario_id)
    ids_obtenidas = {o["insignia_id"] for o in obtenidas}

    por_categoria: dict[str, list[int]] = {}
    for insignia in catalogo:
        categoria = insignia.get("categoria", "otras")
        por_categoria.setdefault(categoria, []).append(insignia["id_insignias"])

    if not por_categoria:
        return 0.0

    porcentajes = []
    for ids_categoria in por_categoria.values():
        total = len(ids_categoria)
        if total == 0:
            continue
        obtenidas_en_categoria = sum(1 for i in ids_categoria if i in ids_obtenidas)
        porcentajes.append((obtenidas_en_categoria / total) * 100)

    return sum(porcentajes) / len(porcentajes) if porcentajes else 0.0


def _conteo_insignias_por_categoria(usuario_id: int) -> dict:
    repo = InsigniaRepository()
    catalogo = {i["id_insignias"]: i.get("categoria") for i in repo.obtener_catalogo_insignias()}
    obtenidas = repo.obtener_insignias_de_usuario(usuario_id)

    conteo = {"rescate": 0, "reporte": 0, "donacion": 0}
    for o in obtenidas:
        categoria = catalogo.get(o["insignia_id"])
        if categoria in conteo:
            conteo[categoria] += 1
    return conteo

def ya_se_postulo(adopcion_id: int, usuario_id: int) -> bool:
    existente = (
        supabase.table("adopcion_postulacion")
        .select("postulacion_id")
        .eq("adopcion_id_fk", adopcion_id)
        .eq("usuario_id_fk", usuario_id)
        .execute()
        .data
    )
    return len(existente) > 0


def obtener_mi_postulacion(adopcion_id: int, usuario_id: int) -> dict:
    filas = (
        supabase.table("adopcion_postulacion")
        .select("postulacion_id,adopcion_id_fk,usuario_id_fk,fecha_registro,estado")
        .eq("adopcion_id_fk", adopcion_id)
        .eq("usuario_id_fk", usuario_id)
        .execute()
        .data
    )
    if not filas:
        return {"ya_postulado": False, "postulacion": None}

    postulacion = filas[0]
    adopcion = (
        supabase.table("adopcion")
        .select("estado,adoptante_id,contacto_responsable")
        .eq("adopcion_id", adopcion_id)
        .single()
        .execute()
        .data
    ) or {}
    fue_aceptada = (
        adopcion.get("estado") == "completada"
        and postulacion.get("estado") == "aceptada"
        and adopcion.get("adoptante_id") == usuario_id
    )
    postulacion["fue_aceptada"] = fue_aceptada
    postulacion["contacto_responsable"] = (
        adopcion.get("contacto_responsable") if fue_aceptada else None
    )
    return {"ya_postulado": True, "postulacion": postulacion}

def contar_postulaciones(adopcion_id: int) -> int:
    resultado = (
        supabase.table("adopcion_postulacion")
        .select("postulacion_id", count="exact")
        .eq("adopcion_id_fk", adopcion_id)
        .execute()
    )
    return resultado.count or 0

def aprobar_postulacion(
    adopcion_id: int,
    postulacion_id: int,
    usuario_id: int,
    contacto_responsable: str,
) -> dict:
    contacto = contacto_responsable.strip()
    if not contacto:
        raise ValueError("El medio de contacto del responsable es obligatorio.")
    if len(contacto) > 255:
        raise ValueError("El medio de contacto no puede exceder 255 caracteres.")
    _verificar_dueno(adopcion_id, usuario_id)
    return aprobar_postulacion_atomica(
        adopcion_id, postulacion_id, usuario_id, contacto
    )
