from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional

class OrganizacionCreate(BaseModel):
    nombre: str
    registroLegal: str
    tiposAnimales: str
    telefonoEmergencia: str
    correoInstitucional: EmailStr
    fechaFundacion: date
    cuentaBancaria: Optional[str] = None
    descripcion: Optional[str] = None
    categoria: Optional[str] = "refugios" 

class UsuarioCreate(BaseModel):
    correo: EmailStr
    contrasenia: str
    nombre: str
    apellidos: str
    nombre_usuario: str
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
    organizacion: Optional[OrganizacionCreate] = None

class UsuarioLogin(BaseModel):
    identificador: str
    contrasenia: str

class UsuarioResponse(BaseModel):
    usuario_id_pk: int
    correo: str
    nombre: str
    apellidos: str
    nombre_usuario: Optional[str] = None
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
    nombre_usuario: Optional[str] = None 
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

#Hacer públicos a los usuarios
class UsuarioPublicoResponse(BaseModel):
    usuario_id_pk: int
    nombre: str
    apellidos: str
    nombre_usuario: str
    correo: Optional[str] = None
    num_telefono: Optional[str] = None
    foto_perfil: str | None = None
    verificado: bool

class SolicitarCodigoRequest(BaseModel):
    correo: EmailStr

class ConfirmarCodigoRequest(BaseModel):
    correo: EmailStr
    codigo: str

class ActualizarUbicacionRequest(BaseModel):
    latitud: float
    longitud: float

class OrganizacionResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    logo_url: Optional[str] = None
    categoria: Optional[str] = None
    tipos_animales: Optional[str] = None
    cuenta_bancaria: Optional[str] = None
    created_at: datetime
    dueño_id: int

    class Config:
        from_attributes = True

class OrganizacionUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    categoria: Optional[str] = None
    tipos_animales: Optional[str] = None
    cuenta_bancaria: Optional[str] = None
    banco: Optional[str] = None
    titular: Optional[str] = None
    logo_url: Optional[str] = None

    class Config:
        from_attributes = True
