from fastapi import APIRouter, HTTPException, Depends
from .schemas import (
    AdopcionCreate, AdopcionOut,
    PostulacionCreate, PostulacionOut,
    SugerirPreguntasRequest, SugerirPreguntasResponse, UploadImagenResponse,
    AprobarPostulacionRequest,
)
from .service import (
    crear_adopcion,
    listar_adopciones,
    obtener_adopcion,
    eliminar_adopcion,
    sugerir_preguntas,
    crear_postulacion,
    listar_postulaciones,
    calcular_ranking,
    obtener_mi_postulacion,
    contar_postulaciones,
    aprobar_postulacion
)
from app.core.security import get_current_user
from fastapi import UploadFile, File
from .service import subir_imagen as subir_imagen_service
from app.modules.reportes.service import subir_evidencia

router = APIRouter(prefix="/adopciones", tags=["Adopciones"])

@router.post("/{adopcion_id}/imagen", response_model=AdopcionOut)
def subir_imagen(
    adopcion_id: int,
    archivo: UploadFile = File(...),
    usuario_actual: dict = Depends(get_current_user),
):
    try:
        return subir_imagen_service(
            adopcion_id, archivo, usuario_actual["usuario_id_pk"]
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("", response_model=AdopcionOut)
def crear(data: AdopcionCreate, usuario_actual: dict = Depends(get_current_user)):
    try:
        return crear_adopcion(data, usuario_actual["usuario_id_pk"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[AdopcionOut])
def listar():
    try:
        return listar_adopciones()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{adopcion_id}", response_model=AdopcionOut)
def obtener(adopcion_id: int):
    try:
        return obtener_adopcion(adopcion_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{adopcion_id}")
def eliminar(adopcion_id: int, usuario_actual: dict = Depends(get_current_user)):
    try:
        eliminar_adopcion(adopcion_id, usuario_actual["usuario_id_pk"])
        return {"message": "Adopción eliminada"}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/sugerir-preguntas", response_model=SugerirPreguntasResponse)
def sugerir(data: SugerirPreguntasRequest):
    try:
        preguntas = sugerir_preguntas(data)
        return {"preguntas_sugeridas": preguntas}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{adopcion_id}/postulaciones", response_model=PostulacionOut)
def postular(
    adopcion_id: int,
    data: PostulacionCreate,
    usuario_actual: dict = Depends(get_current_user),
):
    try:
        return crear_postulacion(
            adopcion_id, data, usuario_actual["usuario_id_pk"]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        if "23505" in str(e) or "duplicate key" in str(e):
            raise HTTPException(
                status_code=409,
                detail="Ya te has postulado a esta adopción anteriormente.",
            )
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{adopcion_id}/postulaciones", response_model=list[PostulacionOut])
def postulaciones(adopcion_id: int, usuario_actual: dict = Depends(get_current_user)):
    try:
        return listar_postulaciones(adopcion_id, usuario_actual["usuario_id_pk"])
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{adopcion_id}/ranking", response_model=list[PostulacionOut])
@router.post("/{adopcion_id}/ranking", response_model=list[PostulacionOut], deprecated=True)
def ranking(adopcion_id: int, usuario_actual: dict = Depends(get_current_user)):
    try:
        return calcular_ranking(adopcion_id, usuario_actual["usuario_id_pk"])
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{adopcion_id}/mi-postulacion")
def mi_postulacion(adopcion_id: int, usuario_actual: dict = Depends(get_current_user)):
    try:
        return obtener_mi_postulacion(adopcion_id, usuario_actual["usuario_id_pk"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{adopcion_id}/postulaciones/conteo")
@router.get("/{adopcion_id}/conteo-postulaciones", deprecated=True)
def conteo_postulaciones(adopcion_id: int):
    try:
        return {"total": contar_postulaciones(adopcion_id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{adopcion_id}/postulaciones/{postulacion_id}/aprobar")
def aprobar(
    adopcion_id: int,
    postulacion_id: int,
    data: AprobarPostulacionRequest,
    usuario_actual: dict = Depends(get_current_user),
):
    try:
        return aprobar_postulacion(
            adopcion_id,
            postulacion_id,
            usuario_actual["usuario_id_pk"],
            data.contacto_responsable,
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/upload-imagen", response_model=UploadImagenResponse)
async def upload_imagen(
    file: UploadFile = File(...),
    usuario_actual: dict = Depends(get_current_user),
):
    try:
        contenido = await file.read()
        url = subir_evidencia(contenido, file.filename)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
