from fastapi import APIRouter, HTTPException, UploadFile, File
from .schemas import ReporteCreate, UploadResponse
from .service import crear_reporte, subir_evidencia, listar_reportes

router = APIRouter(prefix="/reportes", tags=["Reportes"])

@router.post("")
def crear(data: ReporteCreate):
    try:
        return crear_reporte(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/upload_evidencia", response_model=UploadResponse)
async def upload_evidencia(file: UploadFile = File(...)):
    try:
        contenido = await file.read()
        url = subir_evidencia(contenido, file.filename)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
@router.get("")  # ✅ Agregar este endpoint nuevo
def listar():
    try:
        return listar_reportes()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))