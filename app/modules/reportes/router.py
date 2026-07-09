from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from .schemas import ReporteCreate, UploadResponse
from .service import crear_reporte, subir_evidencia, listar_reportes
from app.core.security import get_current_user

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
    
@router.get("") 
def listar(usuario_actual: dict = Depends(get_current_user)):
    try:
        return listar_reportes(usuario_verificado=usuario_actual["verificado"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))