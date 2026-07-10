from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from .schemas import ReporteCreate, UploadResponse, ActualizarEstadoRequest
from .service import crear_reporte, subir_evidencia, listar_reportes, obtener_estado_reporte, actualizar_estado_reporte

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
def listar():
    try:
        return listar_reportes()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{reporte_id}/estado")
def obtener_estado(reporte_id: int):
    """Obtiene el estado actual del reporte con su historial."""
    try:
        return obtener_estado_reporte(reporte_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{reporte_id}/estado")
async def actualizar_estado(
    reporte_id: int,
    nueva_fase_id: int = Form(...),
    usuario_id: int = Form(None),
    evidencia: UploadFile = File(...),
    comentarios: str = Form(None)
):
    """Actualiza el estado del reporte y sube nueva evidencia."""
    try:
        contenido = await evidencia.read()
        resultado = actualizar_estado_reporte(
            reporte_id=reporte_id,
            nueva_fase_id=nueva_fase_id,
            file_bytes=contenido,
            filename=evidencia.filename,
            usuario_id=usuario_id,
            comentarios=comentarios
        )
        return resultado
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))