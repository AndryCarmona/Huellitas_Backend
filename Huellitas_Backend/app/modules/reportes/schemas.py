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
    evidencia: Optional[str]
    usuario_id_fk: int

class ReporteOut(ReporteCreate):
    reporte_id: int
    fecha_reporte: datetime