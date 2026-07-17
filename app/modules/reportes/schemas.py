from pydantic import BaseModel
from datetime import datetime
from typing import Optional,List

class ReporteCreate(BaseModel):
    tipo_animal: int
    raza_id: str
    tamano: str
    descripcion: str
    ubicacion: str
    tipo_reporte: int
    urgencia_id: int
    evidencia: str
    usuario_id_fk: int
    latitud: float
    longitud: float

class ReporteOut(ReporteCreate):
    reporte_id: int
    fecha_reporte: datetime

class UploadResponse(BaseModel):
    url: str

class HistorialFaseOut(BaseModel):
    fase_nombre: str
    fecha_cambio: datetime
    evidencia_url: Optional[str] = None
    comentarios:Optional[str] = None
    usuario_nombre:Optional[str] = None

class ReporteEstadoOut(BaseModel):
    reporteId: int
    faseActual: int
    nivelUrgencia: str
    tipoReporte: str
    descripcion: str
    ubicacion: str
    tipoAnimal: str
    raza: str
    tamano: str
    evidenciaUrl: Optional[str] = None
    historialFases: List[str] = []
    comentarios: Optional[str] = None

class ActualizarEstadoRequest(BaseModel):
    nueva_fase_id: int
    comentarios: Optional[str] = None