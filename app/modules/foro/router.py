from fastapi import APIRouter, HTTPException, status, Depends, Query, UploadFile, File, Form
from typing import Optional, List
from .schemas import (PublicacionResponse, CrearPublicacionRequest, ActualizarPublicacionRequest, PaginaPublicaciones,ComentarioResponse, CrearComentarioRequest, PaginaComentarios,GrupoResponse, CrearGrupoRequest, MiembroGrupoResponse, ResponderSolicitudRequest, EliminarMiembroRequest,ActualizarGrupoRequest)
from .service import PublicacionService, ComentarioService, GrupoService
from app.core.security import get_current_user

router = APIRouter(tags=["Foro"])


# ============ PUBLICACIONES ============
@router.get("/publicaciones/feed", response_model=PaginaPublicaciones)
def obtener_feed(
    categoria: Optional[str] = None,
    grupo_id: Optional[int] = None,
    cursor: Optional[str] = None,
    limite: int = Query(default=20, le=100),
    usuario_actual: dict = Depends(get_current_user),
):
    service = PublicacionService()
    try:
        return service.obtener_feed(
            usuario_id=usuario_actual["usuario_id_pk"],
            categoria=categoria,
            grupo_id=grupo_id,
            cursor=int(cursor) if cursor else None,
            limite=limite,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener feed: {str(e)}")

@router.get("/publicaciones/{publicacion_id}", response_model=PublicacionResponse)
def obtener_publicacion(
    publicacion_id: int,
    usuario_actual: dict = Depends(get_current_user),
):
    service = PublicacionService()
    try:
        return service.obtener_por_id(publicacion_id, usuario_actual["usuario_id_pk"])
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/publicaciones", response_model=PublicacionResponse, status_code=status.HTTP_201_CREATED)
def crear_publicacion(
    titulo: str = Form(...),
    contenido: str = Form(...),
    categoria: Optional[str] = Form(None),
    grupo_id: Optional[int] = Form(None),
    imagen: Optional[UploadFile] = File(None),
    usuario_actual: dict = Depends(get_current_user),
):
    service = PublicacionService()
    try:
        data = CrearPublicacionRequest(
            titulo=titulo,
            contenido=contenido,
            categoria=categoria,
            grupo_id=grupo_id,
        )
        return service.crear_publicacion(data, usuario_actual["usuario_id_pk"], imagen)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear: {str(e)}")

@router.patch("/publicaciones/{publicacion_id}", response_model=PublicacionResponse)
def actualizar_publicacion(
    publicacion_id: int,
    titulo: Optional[str] = Form(None),
    contenido: Optional[str] = Form(None),
    categoria: Optional[str] = Form(None),
    imagen: Optional[UploadFile] = File(None),
    usuario_actual: dict = Depends(get_current_user),
):
    service = PublicacionService()
    try:
        data = ActualizarPublicacionRequest(
            titulo=titulo,
            contenido=contenido,
            categoria=categoria,
        )
        return service.actualizar_publicacion(
            publicacion_id, data, usuario_actual["usuario_id_pk"], imagen
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/publicaciones/{publicacion_id}")
def eliminar_publicacion(
    publicacion_id: int,
    usuario_actual: dict = Depends(get_current_user),
):
    service = PublicacionService()
    try:
        return service.eliminar_publicacion(publicacion_id, usuario_actual["usuario_id_pk"])
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/publicaciones/{publicacion_id}/me-gusta", response_model=PublicacionResponse)
def toggle_me_gusta(
    publicacion_id: int,
    usuario_actual: dict = Depends(get_current_user),
):
    service = PublicacionService()
    try:
        return service.toggle_me_gusta(publicacion_id, usuario_actual["usuario_id_pk"])
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============ COMENTARIOS ============

@router.get("/publicaciones/{publicacion_id}/comentarios", response_model=PaginaComentarios)
def obtener_comentarios(
    publicacion_id: int,
    cursor: Optional[str] = None,
    limite: int = Query(default=30, le=100),
    usuario_actual: dict = Depends(get_current_user),
):
    service = ComentarioService()
    try:
        return service.obtener_comentarios(
            publicacion_id,
            usuario_actual["usuario_id_pk"],
            int(cursor) if cursor else None,
            limite,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/comentarios", response_model=ComentarioResponse, status_code=201)
def crear_comentario(
    data: CrearComentarioRequest,
    usuario_actual: dict = Depends(get_current_user),
):
    service = ComentarioService()
    try:
        return service.crear_comentario(data, usuario_actual["usuario_id_pk"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/comentarios/{comentario_id}", response_model=ComentarioResponse)
def actualizar_comentario(
    comentario_id: int,
    contenido: str,
    usuario_actual: dict = Depends(get_current_user),
):
    service = ComentarioService()
    try:
        return service.actualizar_comentario(
            comentario_id, contenido, usuario_actual["usuario_id_pk"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/comentarios/{comentario_id}")
def eliminar_comentario(
    comentario_id: int,
    usuario_actual: dict = Depends(get_current_user),
):
    service = ComentarioService()
    try:
        return service.eliminar_comentario(comentario_id, usuario_actual["usuario_id_pk"])
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============ GRUPOS ============

@router.get("/grupos", response_model=List[GrupoResponse])
def obtener_grupos(
    busqueda: Optional[str] = None,
    cursor: Optional[str] = None,
    limite: int = Query(default=20, le=100),
    usuario_actual: dict = Depends(get_current_user),
):
    service = GrupoService()
    try:
        return service.obtener_grupos(
            usuario_actual["usuario_id_pk"], busqueda,
            int(cursor) if cursor else None, limite
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/grupos/mis-grupos", response_model=List[GrupoResponse])
def obtener_mis_grupos(usuario_actual: dict = Depends(get_current_user)):
    service = GrupoService()
    return service.obtener_mis_grupos(usuario_actual["usuario_id_pk"])

@router.get("/grupos/{grupo_id}", response_model=GrupoResponse)
def obtener_grupo(grupo_id: int, usuario_actual: dict = Depends(get_current_user)):
    service = GrupoService()
    try:
        return service.obtener_por_id(grupo_id, usuario_actual["usuario_id_pk"])
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

from fastapi import APIRouter, HTTPException, status, Depends, Query, UploadFile, File, Form

@router.post("/grupos", response_model=GrupoResponse, status_code=201)
def crear_grupo(
    nombre: str = Form(...),
    descripcion: str = Form(""),
    privacidad: str = Form("publico"),
    foto_perfil: Optional[UploadFile] = File(None),
    foto_portada: Optional[UploadFile] = File(None),
    usuario_actual: dict = Depends(get_current_user),
):
    service = GrupoService()
    try:
        data = CrearGrupoRequest(
            nombre=nombre,
            descripcion=descripcion,
            privacidad=privacidad,
        )
        return service.crear_grupo(
            data, usuario_actual["usuario_id_pk"],
            foto_perfil, foto_portada
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/grupos/{grupo_id}", response_model=GrupoResponse)
def actualizar_grupo(
    grupo_id: int,
    nombre: Optional[str] = Form(None),
    descripcion: Optional[str] = Form(None),
    privacidad: Optional[str] = Form(None),
    foto_perfil: Optional[UploadFile] = File(None),
    foto_portada: Optional[UploadFile] = File(None),
    usuario_actual: dict = Depends(get_current_user),
):
    service = GrupoService()
    try:
        data = ActualizarGrupoRequest(
            nombre=nombre,
            descripcion=descripcion,
            privacidad=privacidad,
        )
        return service.actualizar_grupo(
            grupo_id, data, usuario_actual["usuario_id_pk"],
            foto_perfil, foto_portada
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/grupos/{grupo_id}/imagenes", response_model=GrupoResponse)
def actualizar_imagenes_grupo(
    grupo_id: int,
    foto_perfil: Optional[UploadFile] = File(None),
    foto_portada: Optional[UploadFile] = File(None),
    usuario_actual: dict = Depends(get_current_user),
):
    service = GrupoService()
    try:
        return service.actualizar_imagenes_grupo(
            grupo_id, usuario_actual["usuario_id_pk"],
            foto_perfil, foto_portada
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/grupos/{grupo_id}/unirse", response_model=GrupoResponse)
def unirse_a_grupo(grupo_id: int, usuario_actual: dict = Depends(get_current_user)):
    service = GrupoService()
    try:
        return service.unirse_a_grupo(grupo_id, usuario_actual["usuario_id_pk"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/grupos/{grupo_id}/solicitar", response_model=GrupoResponse)
def solicitar_ingreso(grupo_id: int, usuario_actual: dict = Depends(get_current_user)):
    service = GrupoService()
    try:
        return service.solicitar_ingreso(grupo_id, usuario_actual["usuario_id_pk"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/grupos/{grupo_id}/solicitud")
def cancelar_solicitud(grupo_id: int, usuario_actual: dict = Depends(get_current_user)):
    service = GrupoService()
    try:
        return service.cancelar_solicitud(grupo_id, usuario_actual["usuario_id_pk"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/grupos/{grupo_id}/salir", response_model=GrupoResponse)
def salir_de_grupo(grupo_id: int, usuario_actual: dict = Depends(get_current_user)):
    service = GrupoService()
    return service.salir_de_grupo(grupo_id, usuario_actual["usuario_id_pk"])

@router.get("/grupos/{grupo_id}/solicitudes", response_model=List[MiembroGrupoResponse])
def obtener_solicitudes(grupo_id: int, usuario_actual: dict = Depends(get_current_user)):
    service = GrupoService()
    try:
        return service.obtener_solicitudes(grupo_id, usuario_actual["usuario_id_pk"])
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.post("/grupos/{grupo_id}/solicitudes/responder")
def responder_solicitud(
    grupo_id: int,
    data: ResponderSolicitudRequest,
    usuario_actual: dict = Depends(get_current_user),
):
    service = GrupoService()
    try:
        return service.responder_solicitud(
            grupo_id, data.usuario_id, data.aceptar, usuario_actual["usuario_id_pk"]
        )
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.post("/grupos/{grupo_id}/miembros/eliminar")
def eliminar_miembro(
    grupo_id: int,
    data: EliminarMiembroRequest,
    usuario_actual: dict = Depends(get_current_user),
):
    service = GrupoService()
    try:
        return service.eliminar_miembro(
            grupo_id, data.usuario_id, usuario_actual["usuario_id_pk"]
        )
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))