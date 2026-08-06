from fastapi import APIRouter
from .service import (
    get_tipos_animal,
    get_tipos_reporte,
    get_urgencias
)

router = APIRouter(prefix="/catalogos", tags=["Catálogos"])

@router.get("/tipos-animal")
def tipos_animal():
    return get_tipos_animal()

@router.get("/tipos-reporte")
def tipos_reporte():
    return get_tipos_reporte()

@router.get("/urgencias")
def urgencias():
    return get_urgencias()