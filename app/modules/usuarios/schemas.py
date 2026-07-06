from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional

class UsuarioCreate(BaseModel):
    correo: EmailStr
    contrasenia: str
    nombre: str
    apellidos: str
    num_telefono: str
    fecha_nacimiento: date
    calle: Optional[str] = None
    colonia: Optional[str] = None
    cp: Optional[str] = None
    ciudad: Optional[str] = None
    estado: Optional[str] = None
    identificacion_frontal: Optional[str] = None
    identificacion_trasera: Optional[str] = None
    foto_selfie: Optional[str] = None

class UsuarioLogin(BaseModel):
    correo: EmailStr
    contrasenia: str

class UsuarioResponse(BaseModel):
    usuario_id_pk: int
    correo: str
    nombre: str
    apellidos: str
    num_telefono: str
    fecha_nacimiento: date
    verificado: bool
    fecha_registro_usuario: datetime
    rol_usuario: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str