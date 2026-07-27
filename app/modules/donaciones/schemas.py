from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class OrganizacionResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str
    logoUrl: str = Field(alias="logo_url")
    categoria: str
    cuentaBancaria: str = Field(alias="cuenta_bancaria")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class DonacionCreate(BaseModel):
    usuarioId: int = Field(alias="usuario_id")
    organizacionId: int = Field(alias="organizacion_id")
    monto: float
    numeroTarjeta: str = Field(alias="numero_tarjeta")
    titularTarjeta: str = Field(alias="titular_tarjeta")
    cvv: str
    fechaVencimiento: str = Field(alias="fecha_vencimiento")

    model_config = ConfigDict(populate_by_name=True)

class DonacionResponse(BaseModel):
    id: int
    usuarioId: int = Field(alias="usuario_id")
    organizacionId: int = Field(alias="organizacion_id")
    monto: float
    numeroTarjeta: str = Field(alias="numero_tarjeta")
    titularTarjeta: str = Field(alias="titular_tarjeta")
    cvv: str
    fechaVencimiento: str = Field(alias="fecha_vencimiento")
    fechaDonacion: datetime = Field(alias="fecha_donacion")
    estado: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)