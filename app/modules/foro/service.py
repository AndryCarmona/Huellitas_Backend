from datetime import datetime
from fastapi import UploadFile
from typing import List
from .repository import PublicacionRepository, ComentarioRepository, GrupoRepository
from .schemas import (CrearPublicacionRequest, ActualizarPublicacionRequest, CrearComentarioRequest, CrearGrupoRequest,ActualizarGrupoRequest)
from app.core.database import supabase

BUCKET_PUBLICACIONES = "publicaciones"
BUCKET_GRUPOS = "grupos"

# ============ PUBLICACIONES ============
class PublicacionService:
    def __init__(self):
        self.repository = PublicacionRepository()

    def _subir_imagen_publicacion(self, usuario_id: int, publicacion_id: int, archivo: UploadFile) -> str:
        contenido = archivo.file.read()
        extension = archivo.filename.split(".")[-1].lower()
        if extension not in ("jpg", "jpeg", "png", "webp", "gif"):
            raise ValueError("Formato de imagen no válido. Usa JPG, PNG, WEBP o GIF")
        ruta = f"{usuario_id}/{publicacion_id}.{extension}"
        supabase.storage.from_(BUCKET_PUBLICACIONES).upload(
            ruta, contenido,
            {"content-type": archivo.content_type or "image/jpeg", "upsert": "true"}
        )
        return supabase.storage.from_(BUCKET_PUBLICACIONES).get_public_url(ruta)

    def _enriquecer_publicacion(self, pub: dict, usuario_id: int) -> dict:
        # ... (igual que antes, sin cambios) ...
        usuario = supabase.table("usuario").select(
            "nombre, foto_perfil"
        ).eq("usuario_id_pk", pub.get("usuario_id")).execute()
        u_data = usuario.data[0] if usuario.data else {"nombre": "Desconocido", "foto_perfil": None}

        grupo_nombre = None
        if pub.get("grupo_id_fk"):
            g = supabase.table("grupo").select("nombre").eq(
                "grupo_id", pub["grupo_id_fk"]
            ).execute()
            if g.data:
                grupo_nombre = g.data[0]["nombre"]

        return {
            **pub,
            "nombre_usuario": u_data["nombre"],
            "foto_usuario": u_data.get("foto_perfil"),
            "nombre_grupo": grupo_nombre,
            "me_gusta": self.repository.obtener_me_gusta_count(pub["publicacion_id"]),
            "comentarios": self.repository.obtener_comentarios_count(pub["publicacion_id"]),
            "le_gusta_al_usuario": self.repository.usuario_le_gusta(
                pub["publicacion_id"], usuario_id
            ),
        }

    def obtener_feed(self, usuario_id: int, categoria: str = None,
                     grupo_id: int = None, cursor: int = None, limite: int = 20):
        # ... (igual que antes) ...
        publicaciones = self.repository.obtener_feed(categoria, grupo_id, cursor, limite + 1)
        hay_mas = len(publicaciones) > limite
        elementos = publicaciones[:limite]
        siguiente = str(elementos[-1]["publicacion_id"]) if hay_mas and elementos else None

        return {
            "elementos": [self._enriquecer_publicacion(p, usuario_id) for p in elementos],
            "siguiente_cursor": siguiente,
            "hay_mas": hay_mas,
        }

    def obtener_por_id(self, publicacion_id: int, usuario_id: int):
        # ... (igual que antes) ...
        pub = self.repository.obtener_por_id(publicacion_id)
        if not pub or pub["estado"] == "eliminada":
            raise ValueError("Publicación no encontrada")
        return self._enriquecer_publicacion(pub, usuario_id)

    # ---------- MODIFICADO: ahora acepta imagen ----------
    def crear_publicacion(self, data: CrearPublicacionRequest, usuario_id: int,
                          imagen: UploadFile = None):
        payload = {
            "usuario_id": usuario_id,
            "titulo": data.titulo,
            "contenido": data.contenido,
        }
        if data.categoria is not None:
            payload["categoria"] = data.categoria
        if data.grupo_id is not None:
            payload["grupo_id_fk"] = data.grupo_id

        # 1. Crear la publicación primero
        pub = self.repository.crear_publicacion(payload)
        publicacion_id = pub["publicacion_id"]

        # 2. Si viene imagen, subirla y actualizar el registro
        if imagen is not None and imagen.filename:
            try:
                url = self._subir_imagen_publicacion(usuario_id, publicacion_id, imagen)
                self.repository.actualizar_publicacion(publicacion_id, {"imagen_url": url})
                pub["imagen_url"] = url
            except Exception as e:
                # Si falla la subida, eliminamos la publicación huérfana
                self.repository.actualizar_publicacion(publicacion_id, {
                    "estado": "eliminada",
                    "fecha_eliminacion": datetime.utcnow().isoformat(),
                })
                raise ValueError(f"Error al subir imagen: {str(e)}")

        return self._enriquecer_publicacion(pub, usuario_id)

    # ---------- MODIFICADO: ahora acepta nueva imagen ----------
    def actualizar_publicacion(self, publicacion_id: int, data: ActualizarPublicacionRequest,
                               usuario_id: int, imagen: UploadFile = None):
        pub = self.repository.obtener_por_id(publicacion_id)
        if not pub:
            raise ValueError("Publicación no encontrada")
        if pub["usuario_id"] != usuario_id:
            raise ValueError("No tienes permiso para editar esta publicación")

        updates = {k: v for k, v in data.dict().items() if v is not None}
        updates["fecha_actualizacion"] = datetime.utcnow().isoformat()

        # Si viene nueva imagen, subirla
        if imagen is not None and imagen.filename:
            url = self._subir_imagen_publicacion(usuario_id, publicacion_id, imagen)
            updates["imagen_url"] = url

        if not updates or updates == {"fecha_actualizacion": updates["fecha_actualizacion"]}:
            raise ValueError("No se enviaron campos para actualizar")

        actualizada = self.repository.actualizar_publicacion(publicacion_id, updates)
        return self._enriquecer_publicacion(actualizada, usuario_id)

    # ... eliminar_publicacion, toggle_me_gusta igual que antes ...

        updates = {k: v for k, v in data.dict().items() if v is not None}
        if not updates:
            raise ValueError("No se enviaron campos para actualizar")
        updates["fecha_actualizacion"] = datetime.utcnow().isoformat()

        actualizada = self.repository.actualizar_publicacion(publicacion_id, updates)
        return self._enriquecer_publicacion(actualizada, usuario_id)

    def eliminar_publicacion(self, publicacion_id: int, usuario_id: int):
        pub = self.repository.obtener_por_id(publicacion_id)
        if not pub:
            raise ValueError("Publicación no encontrada")
        if pub["usuario_id"] != usuario_id:
            raise ValueError("No tienes permiso para eliminar esta publicación")

        self.repository.actualizar_publicacion(publicacion_id, {
            "estado": "eliminada",
            "fecha_eliminacion": datetime.utcnow().isoformat(),
        })
        return {"mensaje": "Publicación eliminada"}

    def toggle_me_gusta(self, publicacion_id: int, usuario_id: int):
        pub = self.repository.obtener_por_id(publicacion_id)
        if not pub or pub["estado"] == "eliminada":
            raise ValueError("Publicación no encontrada")
        self.repository.toggle_me_gusta(publicacion_id, usuario_id)
        return self._enriquecer_publicacion(pub, usuario_id)


# ============ COMENTARIOS ============
class ComentarioService:
    def __init__(self):
        self.repository = ComentarioRepository()

    def _enriquecer_comentario(self, c: dict, usuario_id: int) -> dict:
        usuario = supabase.table("usuario").select(
            "nombre, foto_perfil"
        ).eq("usuario_id_pk", c.get("usuario_id_fk")).execute()
        u_data = usuario.data[0] if usuario.data else {"nombre": "Desconocido", "foto_perfil": None}

        return {
            **c,
            "nombre_usuario": u_data["nombre"],
            "foto_usuario": u_data.get("foto_perfil"),
            "cantidad_me_gusta": 0,
            "le_gusta_al_usuario": False,
        }

    def obtener_comentarios(self, publicacion_id: int, usuario_id: int,
                            cursor: int = None, limite: int = 30):
        comentarios = self.repository.obtener_comentarios(publicacion_id, cursor, limite + 1)
        hay_mas = len(comentarios) > limite
        elementos = comentarios[:limite]
        siguiente = str(elementos[-1]["comentario_id"]) if hay_mas and elementos else None

        return {
            "elementos": [self._enriquecer_comentario(c, usuario_id) for c in elementos],
            "siguiente_cursor": siguiente,
            "hay_mas": hay_mas,
        }

    def crear_comentario(self, data: CrearComentarioRequest, usuario_id: int):
        payload = {
            "publicacion_id_fk": data.publicacion_id,
            "usuario_id_fk": usuario_id,
            "contenido": data.contenido,
        }
        if data.comentario_padre_id is not None:
            payload["comentario_padre_id"] = data.comentario_padre_id
        c = self.repository.crear_comentario(payload)
        return self._enriquecer_comentario(c, usuario_id)

    def actualizar_comentario(self, comentario_id: int, contenido: str, usuario_id: int):
        c = self.repository.obtener_por_id(comentario_id)
        if not c:
            raise ValueError("Comentario no encontrado")
        if c["usuario_id_fk"] != usuario_id:
            raise ValueError("No tienes permiso para editar este comentario")

        actualizado = self.repository.actualizar_comentario(comentario_id, {
            "contenido": contenido,
            "fecha_edicion": datetime.utcnow().isoformat(),
        })
        return self._enriquecer_comentario(actualizado, usuario_id)

    def eliminar_comentario(self, comentario_id: int, usuario_id: int):
        c = self.repository.obtener_por_id(comentario_id)
        if not c:
            raise ValueError("Comentario no encontrado")
        if c["usuario_id_fk"] != usuario_id:
            raise ValueError("No tienes permiso para eliminar este comentario")

        self.repository.actualizar_comentario(comentario_id, {
            "estado": "eliminado",
            "fecha_eliminacion": datetime.utcnow().isoformat(),
        })
        return {"mensaje": "Comentario eliminado"}

# ============ GRUPOS ============

class GrupoService:
    def __init__(self):
        self.repository = GrupoRepository()

    def _subir_imagen_grupo(self, grupo_id: int, archivo: UploadFile,
                            tipo: str) -> str:
        """tipo debe ser 'perfil' o 'portada'"""
        if tipo not in ("perfil", "portada"):
            raise ValueError("Tipo de imagen inválido")
        contenido = archivo.file.read()
        extension = archivo.filename.split(".")[-1].lower()
        if extension not in ("jpg", "jpeg", "png", "webp", "gif"):
            raise ValueError("Formato de imagen no válido. Usa JPG, PNG, WEBP o GIF")
        ruta = f"{grupo_id}/{tipo}.{extension}"
        supabase.storage.from_(BUCKET_GRUPOS).upload(
            ruta, contenido,
            {"content-type": archivo.content_type or "image/jpeg", "upsert": "true"}
        )
        return supabase.storage.from_(BUCKET_GRUPOS).get_public_url(ruta)

    def _enriquecer_grupo(self, g: dict, usuario_id: int) -> dict:
        miembros = self.repository.obtener_miembros(g["grupo_id"])
        membresia = self.repository.obtener_miembro(g["grupo_id"], usuario_id)

        solicitud_pendiente = False
        es_miembro = False
        es_admin = False
        if membresia:
            if membresia["estado"] == "activa":
                es_miembro = True
                es_admin = membresia["rol"] == "administrador"
            elif membresia["estado"] == "pendiente":
                solicitud_pendiente = True

        return {
            **g,
            "cantidad_miembros": len(miembros),
            "es_miembro": es_miembro,
            "es_administrador_actual": es_admin,
            "solicitud_pendiente": solicitud_pendiente,
        }

    def obtener_grupos(self, usuario_id: int, busqueda: str = None, cursor: int = None, limite: int = 20):
        grupos = self.repository.obtener_grupos(busqueda, cursor, limite)
        return [self._enriquecer_grupo(g, usuario_id) for g in grupos]

    def obtener_mis_grupos(self, usuario_id: int):
        grupos = self.repository.obtener_mis_grupos(usuario_id)
        return [self._enriquecer_grupo(g, usuario_id) for g in grupos]

    def obtener_por_id(self, grupo_id: int, usuario_id: int):
        g = self.repository.obtener_por_id(grupo_id)
        if not g or g["estado"] == "eliminado":
            raise ValueError("Grupo no encontrado")
        return self._enriquecer_grupo(g, usuario_id)

    def crear_grupo(self, data: CrearGrupoRequest, usuario_id: int, foto_perfil: UploadFile = None, foto_portada: UploadFile = None):
        grupo = self.repository.crear_grupo({
            "creador_usuario": usuario_id,
            "nombre": data.nombre,
            "descripcion": data.descripcion,
            "privacidad": data.privacidad,
        })
        grupo_id = grupo["grupo_id"]

        try:
            if foto_perfil is not None and foto_perfil.filename:
                url = self._subir_imagen_grupo(grupo_id, foto_perfil, "perfil")
                grupo["foto_perfil"] = url

            if foto_portada is not None and foto_portada.filename:
                url = self._subir_imagen_grupo(grupo_id, foto_portada, "portada")
                grupo["foto_portada"] = url

            if grupo.get("foto_perfil") or grupo.get("foto_portada"):
                updates = {}
                if grupo.get("foto_perfil"):
                    updates["foto_perfil"] = grupo["foto_perfil"]
                if grupo.get("foto_portada"):
                    updates["foto_portada"] = grupo["foto_portada"]
                self.repository.actualizar_grupo(grupo_id, updates)

        except Exception as e:
            supabase.table("grupo").update({
                "estado": "eliminado",
                "fecha_actualizacion": datetime.utcnow().isoformat(),
            }).eq("grupo_id", grupo_id).execute()
            raise ValueError(f"Error al subir imágenes: {str(e)}")

        self.repository.crear_miembro({
            "grupo_id_fk": grupo_id,
            "usuario_id_fk": usuario_id,
            "rol": "administrador",
            "estado": "activa",
            "fecha_ingreso": datetime.utcnow().isoformat(),
        })
        return self._enriquecer_grupo(grupo, usuario_id)

    def actualizar_imagenes_grupo(self, grupo_id: int, usuario_id: int, foto_perfil: UploadFile = None, foto_portada: UploadFile = None):
        g = self.repository.obtener_por_id(grupo_id)
        if not g or g["estado"] == "eliminado":
            raise ValueError("Grupo no encontrado")
        if g["creador_usuario"] != usuario_id:
            miembro = self.repository.obtener_miembro(grupo_id, usuario_id)
            if not miembro or miembro["rol"] != "administrador":
                raise ValueError("No tienes permiso para editar este grupo")

        updates = {}
        if foto_perfil is not None and foto_perfil.filename:
            updates["foto_perfil"] = self._subir_imagen_grupo(grupo_id, foto_perfil, "perfil")
        if foto_portada is not None and foto_portada.filename:
            updates["foto_portada"] = self._subir_imagen_grupo(grupo_id, foto_portada, "portada")

        if not updates:
            raise ValueError("No se enviaron imágenes para actualizar")

        updates["fecha_actualizacion"] = datetime.utcnow().isoformat()
        actualizado = self.repository.actualizar_grupo(grupo_id, updates)
        return self._enriquecer_grupo(actualizado, usuario_id)

    def actualizar_grupo(self, grupo_id: int, data: ActualizarGrupoRequest, usuario_id: int, foto_perfil: UploadFile = None, foto_portada: UploadFile = None):
        g = self.repository.obtener_por_id(grupo_id)
        if not g or g["estado"] == "eliminado":
            raise ValueError("Grupo no encontrado")
        
        miembro = self.repository.obtener_miembro(grupo_id, usuario_id)
        if not miembro or miembro["rol"] != "administrador":
            raise ValueError("Solo los administradores pueden editar el grupo")

        updates = {k: v for k, v in data.dict().items() if v is not None}

        try:
            if foto_perfil is not None and foto_perfil.filename:
                updates["foto_perfil"] = self._subir_imagen_grupo(grupo_id, foto_perfil, "perfil")
            if foto_portada is not None and foto_portada.filename:
                updates["foto_portada"] = self._subir_imagen_grupo(grupo_id, foto_portada, "portada")
        except Exception as e:
            raise ValueError(f"Error al subir imágenes: {str(e)}")

        if not updates:
            raise ValueError("No se enviaron campos para actualizar")

        updates["fecha_actualizacion"] = datetime.utcnow().isoformat()
        actualizado = self.repository.actualizar_grupo(grupo_id, updates)
        return self._enriquecer_grupo(actualizado, usuario_id)
    
    def unirse_a_grupo(self, grupo_id: int, usuario_id: int):
        g = self.repository.obtener_por_id(grupo_id)
        if not g:
            raise ValueError("Grupo no encontrado")
        if g["privacidad"] == "privado":
            raise ValueError("Este grupo es privado, solicita ingreso")
        self.repository.crear_miembro({
            "grupo_id_fk": grupo_id,
            "usuario_id_fk": usuario_id,
            "rol": "miembro",
            "estado": "activa",
            "fecha_ingreso": datetime.utcnow().isoformat(),
        })
        return self._enriquecer_grupo(g, usuario_id)

    def solicitar_ingreso(self, grupo_id: int, usuario_id: int):
        g = self.repository.obtener_por_id(grupo_id)
        if not g:
            raise ValueError("Grupo no encontrado")
        self.repository.crear_miembro({
            "grupo_id_fk": grupo_id,
            "usuario_id_fk": usuario_id,
            "rol": "miembro",
            "estado": "pendiente",
        })
        return self._enriquecer_grupo(g, usuario_id)

    def cancelar_solicitud(self, grupo_id: int, usuario_id: int):
        membresia = self.repository.obtener_miembro(grupo_id, usuario_id)
        if not membresia or membresia["estado"] != "pendiente":
            raise ValueError("No tienes una solicitud pendiente")
        supabase.table("miembros_grupos").delete().eq(
            "miembro_id", membresia["miembro_id"]
        ).execute()
        return {"mensaje": "Solicitud cancelada"}

    def salir_de_grupo(self, grupo_id: int, usuario_id: int):
        self.repository.eliminar_miembro(grupo_id, usuario_id)
        g = self.repository.obtener_por_id(grupo_id)
        return self._enriquecer_grupo(g, usuario_id)

    def obtener_solicitudes(self, grupo_id: int, usuario_id: int):
        membresia = self.repository.obtener_miembro(grupo_id, usuario_id)
        if not membresia or membresia["rol"] != "administrador":
            raise ValueError("Solo los administradores pueden ver solicitudes")
        solicitudes = self.repository.obtener_solicitudes(grupo_id)
        resultado = []
        for s in solicitudes:
            u = s.get("usuario") or {}
            resultado.append({
                "miembro_id": s["miembro_id"],
                "usuario_id_fk": s["usuario_id_fk"],
                "nombre_usuario": u.get("nombre"),
                "foto_usuario": u.get("foto_perfil"),
                "rol": s["rol"],
                "estado": s["estado"],
                "fecha_solicitud": s["fecha_solicitud"],
            })
        return resultado

    def responder_solicitud(self, grupo_id: int, usuario_solicitante: int, aceptar: bool, usuario_admin: int):
        membresia_admin = self.repository.obtener_miembro(grupo_id, usuario_admin)
        if not membresia_admin or membresia_admin["rol"] != "administrador":
            raise ValueError("Solo administradores pueden responder solicitudes")

        if aceptar:
            self.repository.actualizar_miembro(grupo_id, usuario_solicitante, {
                "estado": "activa",
                "fecha_ingreso": datetime.utcnow().isoformat(),
            })
        else:
            membresia_sol = self.repository.obtener_miembro(grupo_id, usuario_solicitante)
            if membresia_sol:
                supabase.table("miembros_grupos").delete().eq("miembro_id", membresia_sol["miembro_id"]).execute()
        return {"mensaje": "Solicitud procesada"}

    def eliminar_miembro(self, grupo_id: int, usuario_id_a_eliminar: int, usuario_admin: int):
        membresia_admin = self.repository.obtener_miembro(grupo_id, usuario_admin)
        if not membresia_admin or membresia_admin["rol"] != "administrador":
            raise ValueError("Solo administradores pueden eliminar miembros")
        self.repository.eliminar_miembro(grupo_id, usuario_id_a_eliminar)
        return {"mensaje": "Miembro eliminado"}

    def obtener_miembros_grupo(self, grupo_id: int, usuario_id: int) -> List[dict]:
        g = self.repository.obtener_por_id(grupo_id)
        if not g or g["estado"] == "eliminado":
            raise ValueError("Grupo no encontrado")

        miembros = self.repository.obtener_miembros(grupo_id)

        usuarios_vistos = set()
        miembros_unicos = []
        for m in miembros:
            if m["usuario_id_fk"] not in usuarios_vistos:
                usuarios_vistos.add(m["usuario_id_fk"])
                miembros_unicos.append(m)

        resultado = []
        for m in miembros_unicos:
            u = supabase.table("usuario").select(
                "nombre, foto_perfil"
            ).eq("usuario_id_pk", m["usuario_id_fk"]).execute()
            u_data = u.data[0] if u.data else {"nombre": "Desconocido", "foto_perfil": None}
            
            resultado.append({
                "miembro_id": m["miembro_id"],
                "usuario_id_fk": m["usuario_id_fk"],
                "nombre_usuario": u_data["nombre"],
                "foto_usuario": u_data.get("foto_perfil"),
                "rol": m["rol"],
                "estado": m["estado"],
                "fecha_solicitud": m.get("fecha_solicitud"),
                "fecha_ingreso": m.get("fecha_ingreso"),
            })
        return resultado