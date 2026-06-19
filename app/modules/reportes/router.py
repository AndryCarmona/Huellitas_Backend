from fastapi import APIRouter, HTTPException
from .schemas import ReporteCreate
from .service import crear_reporte

router = APIRouter(prefix="/reportes", tags=["Reportes"])

@router.post("")
def crear(data: ReporteCreate):
    try:
        return crear_reporte(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))