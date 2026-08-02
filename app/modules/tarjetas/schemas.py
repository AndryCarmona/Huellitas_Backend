from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class TarjetaCreate(BaseModel):
    numeroTarjeta: str = Field(alias="numero_tarjeta")
    titular: str
    fechaVencimiento: str = Field(alias="fecha_vencimiento")
    cvv: str
    tipo: Optional[str] = None
    esPredeterminada: bool = Field(default=False, alias="es_predeterminada")

    model_config = ConfigDict(populate_by_name=True)


class TarjetaUpdate(BaseModel):
    titular: Optional[str] = None
    fechaVencimiento: Optional[str] = Field(default=None, alias="fecha_vencimiento")
    esPredeterminada: Optional[bool] = Field(default=None, alias="es_predeterminada")

    model_config = ConfigDict(populate_by_name=True)


class TarjetaResponse(BaseModel):
    tarjetaId: int = Field(alias="tarjeta_id")
    usuarioId: int = Field(alias="usuario_id")  # Este sí se devuelve en la respuesta
    numeroEnmascarado: str = Field(alias="numero_enmascarado")
    titular: str
    fechaVencimiento: str = Field(alias="fecha_vencimiento")
    tipo: str
    esPredeterminada: bool = Field(alias="es_predeterminada")
    fechaCreacion: datetime = Field(alias="fecha_creacion")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)