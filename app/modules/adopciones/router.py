from fastapi import APIRouter, HTTPException, Depends
from .schemas import (
    AdopcionCreate, AdopcionOut,
    PostulacionCreate, PostulacionOut,
    SugerirPreguntasRequest, SugerirPreguntasResponse,
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
)
from app.core.security import get_current_user

router = APIRouter(prefix="/adopciones", tags=["Adopciones"])


@router.post("", response_model=AdopcionOut)
def crear(data: AdopcionCreate):
    try:
        return crear_adopcion(data)
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
        return crear_postulacion(adopcion_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{adopcion_id}/postulaciones", response_model=list[PostulacionOut])
def postulaciones(adopcion_id: int, usuario_actual: dict = Depends(get_current_user)):
    try:
        return listar_postulaciones(adopcion_id, usuario_actual["usuario_id_pk"])
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{adopcion_id}/ranking", response_model=list[PostulacionOut])
def ranking(adopcion_id: int, usuario_actual: dict = Depends(get_current_user)):
    try:
        return calcular_ranking(adopcion_id, usuario_actual["usuario_id_pk"])
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))