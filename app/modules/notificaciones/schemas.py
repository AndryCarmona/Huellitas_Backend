from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NotificacionResponse(BaseModel):
    id: int
    tipo: str
    titulo: str
    mensaje: str
    data: Optional[dict] = None
    leida: bool
    creada_en: datetime