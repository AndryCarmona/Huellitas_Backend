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
    tarjetaId: int = Field(alias="tarjeta_id")
    metodoPago: str = Field(default="tarjeta", alias="metodo_pago")

    model_config = ConfigDict(populate_by_name=True)

class DonacionResponse(BaseModel):
    id: int
    usuarioId: int = Field(alias="usuario_id")
    organizacionId: int = Field(alias="organizacion_id")
    monto: float
    tarjetaId: int = Field(alias="tarjeta_id")
    metodoPago: str = Field(default="tarjeta", alias="metodo_pago")
    fechaDonacion: datetime = Field(alias="fecha_donacion")
    estado: str
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)