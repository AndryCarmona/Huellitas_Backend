from pydantic import BaseModel
from datetime import datetime
from typing import Optional

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
