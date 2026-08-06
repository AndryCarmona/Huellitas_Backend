from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# ============ PUBLICACIONES ============

class CrearPublicacionRequest(BaseModel):
    titulo: str
    contenido: str
    categoria: Optional[str] = None
    grupo_id: Optional[int] = None

class ActualizarPublicacionRequest(BaseModel):
    titulo: Optional[str] = None
    contenido: Optional[str] = None
    categoria: Optional[str] = None

class PublicacionResponse(BaseModel):
    publicacion_id: int
    usuario_id: Optional[int] = None
    grupo_id_fk: Optional[int] = None
    titulo: str
    nombre_usuario: str
    foto_usuario: Optional[str] = None
    contenido: str
    imagen_url: Optional[str] = None
    categoria: Optional[str] = None
    estado: str
    nombre_grupo: Optional[str] = None
    fecha_publicacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    fecha_eliminacion: Optional[datetime] = None
    me_gusta: int = 0
    comentarios: int = 0
    le_gusta_al_usuario: bool = False

    class Config:
        from_attributes = True

class PaginaPublicaciones(BaseModel):
    elementos: List[PublicacionResponse]
    siguiente_cursor: Optional[str] = None
    hay_mas: bool


# ============ COMENTARIOS ============

class CrearComentarioRequest(BaseModel):
    publicacion_id: int
    contenido: str
    comentario_padre_id: Optional[int] = None

class ComentarioResponse(BaseModel):
    comentario_id: int
    publicacion_id_fk: int
    usuario_id_fk: Optional[int] = None
    comentario_padre_id: Optional[int] = None
    nombre_usuario: str
    foto_usuario: Optional[str] = None
    contenido: str
    estado: str
    fecha_creacion: datetime
    fecha_edicion: Optional[datetime] = None
    fecha_eliminacion: Optional[datetime] = None
    cantidad_me_gusta: int = 0
    le_gusta_al_usuario: bool = False

    class Config:
        from_attributes = True

class PaginaComentarios(BaseModel):
    elementos: List[ComentarioResponse]
    siguiente_cursor: Optional[str] = None
    hay_mas: bool


# ============ GRUPOS ============

class CrearGrupoRequest(BaseModel):
    nombre: str
    descripcion: str = ""
    privacidad: str = "publico"

class GrupoResponse(BaseModel):
    grupo_id: int
    creador_usuario: Optional[int] = None
    nombre: str
    descripcion: str
    foto_perfil: str
    foto_portada: str
    privacidad: str
    estado: str
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    cantidad_miembros: int = 0
    es_miembro: bool = False
    es_administrador_actual: bool = False
    solicitud_pendiente: bool = False

    class Config:
        from_attributes = True

class MiembroGrupoResponse(BaseModel):
    miembro_id: int
    usuario_id_fk: int
    nombre_usuario: Optional[str] = None
    foto_usuario: Optional[str] = None
    rol: str
    estado: str
    fecha_solicitud: Optional[datetime] = None
    fecha_ingreso: Optional[datetime] = None

    class Config:
        from_attributes = True

class ResponderSolicitudRequest(BaseModel):
    usuario_id: int
    aceptar: bool

class EliminarMiembroRequest(BaseModel):
    usuario_id: int

class ActualizarImagenPublicacionRequest(BaseModel):
    imagen_url: str

class ActualizarGrupoRequest(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    privacidad: Optional[str] = None