from app.core.database import supabase

# ============ PUBLICACIONES ============

class PublicacionRepository:

    def obtener_por_id(self, publicacion_id: int):
        result = supabase.table("publicacion").select("*").eq(
            "publicacion_id", publicacion_id
        ).execute()
        return result.data[0] if result.data else None

    def crear_publicacion(self, data: dict):
        result = supabase.table("publicacion").insert(data).execute()
        return result.data[0]

    def actualizar_publicacion(self, publicacion_id: int, data: dict):
        result = supabase.table("publicacion").update(data).eq(
            "publicacion_id", publicacion_id
        ).execute()
        return result.data[0] if result.data else None

    def obtener_feed(self, categoria: str = None, grupo_id: int = None,
                     cursor: int = None, limite: int = 20):
        query = supabase.table("publicacion").select("*").eq("estado", "activa")
        if categoria:
            query = query.eq("categoria", categoria)
        if grupo_id:
            query = query.eq("grupo_id_fk", grupo_id)
        if cursor:
            query = query.lt("publicacion_id", cursor)
        result = query.order("fecha_publicacion", desc=True).limit(limite).execute()
        return result.data or []

    def toggle_me_gusta(self, publicacion_id: int, usuario_id: int):
        existente = supabase.table("reaccion_publicacion").select("*").eq(
            "publicacion_id_fk", publicacion_id
        ).eq("usuario_id_fk", usuario_id).execute()

        if existente.data:
            supabase.table("reaccion_publicacion").delete().eq(
                "reaccion_id", existente.data[0]["reaccion_id"]
            ).execute()
            return False
        else:
            supabase.table("reaccion_publicacion").insert({
                "publicacion_id_fk": publicacion_id,
                "usuario_id_fk": usuario_id,
            }).execute()
            return True

    def obtener_me_gusta_count(self, publicacion_id: int) -> int:
        result = supabase.table("reaccion_publicacion").select(
            "reaccion_id", count="exact"
        ).eq("publicacion_id_fk", publicacion_id).execute()
        return result.count or 0

    def usuario_le_gusta(self, publicacion_id: int, usuario_id: int) -> bool:
        result = supabase.table("reaccion_publicacion").select("*").eq(
            "publicacion_id_fk", publicacion_id
        ).eq("usuario_id_fk", usuario_id).execute()
        return bool(result.data)

    def obtener_comentarios_count(self, publicacion_id: int) -> int:
        result = supabase.table("comentario").select(
            "comentario_id", count="exact"
        ).eq("publicacion_id_fk", publicacion_id).eq("estado", "activo").execute()
        return result.count or 0


# ============ COMENTARIOS ============

class ComentarioRepository:

    def obtener_por_id(self, comentario_id: int):
        result = supabase.table("comentario").select("*").eq(
            "comentario_id", comentario_id
        ).execute()
        return result.data[0] if result.data else None

    def crear_comentario(self, data: dict):
        result = supabase.table("comentario").insert(data).execute()
        return result.data[0]

    def actualizar_comentario(self, comentario_id: int, data: dict):
        result = supabase.table("comentario").update(data).eq(
            "comentario_id", comentario_id
        ).execute()
        return result.data[0] if result.data else None

    def obtener_comentarios(self, publicacion_id: int, cursor: int = None, limite: int = 30):
        query = supabase.table("comentario").select("*").eq(
            "publicacion_id_fk", publicacion_id
        ).eq("estado", "activo")
        if cursor:
            query = query.lt("comentario_id", cursor)
        result = query.order("fecha_creacion", desc=True).limit(limite).execute()
        return result.data or []


# ============ GRUPOS ============

class GrupoRepository:

    def obtener_por_id(self, grupo_id: int):
        result = supabase.table("grupo").select("*").eq(
            "grupo_id", grupo_id
        ).execute()
        return result.data[0] if result.data else None

    def crear_grupo(self, data: dict):
        result = supabase.table("grupo").insert(data).execute()
        return result.data[0]

    def obtener_grupos(self, busqueda: str = None, cursor: int = None, limite: int = 20):
        query = supabase.table("grupo").select("*").eq("estado", "activo")
        if busqueda:
            query = query.ilike("nombre", f"%{busqueda}%")
        if cursor:
            query = query.lt("grupo_id", cursor)
        result = query.order("fecha_creacion", desc=True).limit(limite).execute()
        return result.data or []

    def obtener_mis_grupos(self, usuario_id: int):
        membresias = supabase.table("miembros_grupos").select("grupo_id_fk").eq(
            "usuario_id_fk", usuario_id
        ).eq("estado", "activa").execute()
        if not membresias.data:
            return []
        ids = [m["grupo_id_fk"] for m in membresias.data]
        result = supabase.table("grupo").select("*").in_("grupo_id", ids).execute()
        return result.data or []

    def crear_miembro(self, data: dict):
        result = supabase.table("miembros_grupos").insert(data).execute()
        return result.data[0] if result.data else None

    def actualizar_miembro(self, grupo_id: int, usuario_id: int, data: dict):
        result = supabase.table("miembros_grupos").update(data).eq(
            "grupo_id_fk", grupo_id
        ).eq("usuario_id_fk", usuario_id).execute()
        return result.data[0] if result.data else None

    def obtener_miembro(self, grupo_id: int, usuario_id: int):
        result = supabase.table("miembros_grupos").select("*").eq(
            "grupo_id_fk", grupo_id
        ).eq("usuario_id_fk", usuario_id).execute()
        return result.data[0] if result.data else None

    def obtener_miembros(self, grupo_id: int):
        result = supabase.table("miembros_grupos").select(
            "miembro_id, usuario_id_fk, rol, estado"
        ).eq("grupo_id_fk", grupo_id).eq("estado", "activa").execute()
        return result.data or []

    def obtener_solicitudes(self, grupo_id: int):
        result = supabase.table("miembros_grupos").select(
            "*, usuario:usuario_id_fk(nombre, foto_perfil)"
        ).eq("grupo_id_fk", grupo_id).eq("estado", "pendiente").execute()
        return result.data or []

    def eliminar_miembro(self, grupo_id: int, usuario_id: int):
        result = supabase.table("miembros_grupos").update({
            "estado": "abandono",
            "fecha_salida": "now()",
        }).eq("grupo_id_fk", grupo_id).eq("usuario_id_fk", usuario_id).execute()
        return result.data[0] if result.data else None

    def actualizar_grupo(self, grupo_id: int, data: dict):
        result = supabase.table("grupo").update(data).eq("grupo_id", grupo_id).execute()
        return result.data[0] if result.data else None

    def obtener_por_id(self, grupo_id: int):
        result = (
            supabase.table("grupo")
            .select("*")
            .eq("grupo_id", grupo_id)
            .eq("estado", "activo")
            .execute()
        )
        return result.data[0] if result.data else None

    def eliminar_grupo(self, grupo_id: int):
        result = (
            supabase.table("grupo")
            .update({"estado": "eliminado"})
            .eq("grupo_id", grupo_id)
            .eq("estado", "activo")
            .execute()
        )
        return result.data[0] if result.data else None

    def obtener_mis_grupos(self, usuario_id: int):
        membresias = (
            supabase.table("miembros_grupos")
            .select("grupo_id_fk")
            .eq("usuario_id_fk", usuario_id)
            .eq("estado", "activa")
            .execute()
        )

        if not membresias.data:
            return []

        ids = [m["grupo_id_fk"] for m in membresias.data]

        result = (
            supabase.table("grupo")
            .select("*")
            .in_("grupo_id", ids)
            .eq("estado", "activo")
            .execute()
        )

        return result.data or []