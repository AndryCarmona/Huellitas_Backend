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
    preguntas: List[PreguntaAdopcionOut] = []


class RespuestaCreate(BaseModel):
    pregunta_id: int
    respuesta_texto: str


class RespuestaOut(RespuestaCreate):
    respuesta_id: int
    score_ia: Optional[float] = None
    justificacion_ia: Optional[str] = None


class PostulacionCreate(BaseModel):
    usuario_id_fk: int
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


class SugerirPreguntasRequest(BaseModel):
    especie: str
    edad: str
    tamano: str
    descripcion: Optional[str] = None


class SugerirPreguntasResponse(BaseModel):
    preguntas_sugeridas: List[str]