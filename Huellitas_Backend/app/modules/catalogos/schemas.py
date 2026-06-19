from pydantic import BaseModel

class TipoAnimalOut(BaseModel):
    tipo_animal: int
    nombre: str

class TipoReporteOut(BaseModel):
    tipo_reporte: int
    clasificacion: str

class UrgenciaOut(BaseModel):
    urgencia_id: int
    estado: str