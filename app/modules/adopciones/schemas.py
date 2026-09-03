from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class PreguntaAdopcionCreate(BaseModel):
    texto: str
    criterio_esperado: Optional[str] = None


class PreguntaAdopcionOut(PreguntaAdopcionCreate):
    pregunta_id: int
    orden: int


class AdopcionCreate(BaseModel):
    # Se conserva opcional durante la migracion de clientes antiguos. El servidor
    # siempre sustituye este valor por el usuario autenticado.
    usuario_id_fk: Optional[int] = None
    nombre: str
    especie: str
    edad: str
    tamano: str
    ciudad: str
    sexo: str
    vacunas: str
    descripcion: str
    imagen_url: Optional[str] = None
    preguntas: List[PreguntaAdopcionCreate] = []


class AdopcionOut(BaseModel):
    adopcion_id: int
    usuario_id_fk: int
    nombre: str
    especie: str
    edad: str
    tamano: str
    ciudad: str
    sexo: str
    vacunas: str
    descripcion: str
    imagen_url: Optional[str] = None
    fecha_adopcion: datetime
    estado: str
    adoptante_id: Optional[int] = None
    contacto_responsable: Optional[str] = None
    contacto_adoptante: Optional[str] = None
    preguntas: List[PreguntaAdopcionOut] = []


class RespuestaCreate(BaseModel):
    pregunta_id: int
    respuesta_texto: str


class RespuestaOut(RespuestaCreate):
    respuesta_id: int
    score_ia: Optional[float] = None
    justificacion_ia: Optional[str] = None


class PostulacionCreate(BaseModel):
    # Compatibilidad con Flutter antiguo; no es una fuente de identidad confiable.
    usuario_id_fk: Optional[int] = None
    respuestas: List[RespuestaCreate]


class PostulacionOut(BaseModel):
    postulacion_id: int
    adopcion_id_fk: int
    usuario_id_fk: int
    fecha_registro: datetime
    estado: str
    score_insignias: Optional[float] = None
    score_respuestas_ia: Optional[float] = None
    score_final: Optional[float] = None
    respuestas: List[RespuestaOut] = []
    nombre_usuario: Optional[str] = None
    foto_perfil: Optional[str] = None
    ciudad: Optional[str] = None
    estado_usuario: Optional[str] = None
    fecha_registro_usuario: Optional[datetime] = None
    insignias_rescate: int = 0
    insignias_reporte: int = 0
    insignias_donacion: int = 0
    contacto: Optional[str] = None
    contacto_responsable: Optional[str] = None
    fue_aceptada: bool = False


class AprobarPostulacionRequest(BaseModel):
    contacto_responsable: str


class SugerirPreguntasRequest(BaseModel):
    especie: str
    edad: str
    tamano: str
    descripcion: Optional[str] = None


class SugerirPreguntasResponse(BaseModel):
    preguntas_sugeridas: List[str]

class UploadImagenResponse(BaseModel):
    url: str
