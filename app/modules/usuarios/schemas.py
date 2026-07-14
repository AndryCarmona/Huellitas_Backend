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
    calle: Optional[str] = None
    colonia: Optional[str] = None
    cp: Optional[str] = None
    ciudad: Optional[str] = None
    estado: Optional[str] = None
    foto_perfil: Optional[str] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

#ACTUALIZAR INFO
class EditarPerfilRequest(BaseModel):
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    num_telefono: Optional[str] = None
    calle: Optional[str] = None
    colonia: Optional[str] = None
    cp: Optional[str] = None
    ciudad: Optional[str] = None

class CambiarContraseniaRequest(BaseModel):
    contrasenia_actual: str
    contrasenia_nueva: str

class ActualizarFotoPerfilRequest(BaseModel):
    foto_perfil: str 