from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class CategoriaInsignia(str, Enum):
    rescate = "rescate"
    donacion = "donacion"
    reporte = "reporte"

class InsigniaResponse(BaseModel):
    id: int
    nombre: str
    nivel: int
    categoria: CategoriaInsignia
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    obtenida: bool
    fecha_obtencion: Optional[datetime] = None

    class Config:
        from_attributes = True