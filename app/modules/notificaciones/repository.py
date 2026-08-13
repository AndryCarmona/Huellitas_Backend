from app.core.database import supabase

class NotificacionRepository:
    def crear_notificaciones(self, notificaciones: list[dict]):
        if not notificaciones:
            return []
        result = supabase.table("notificaciones").insert(notificaciones).execute()
        return result.data

    def obtener_por_usuario(self, usuario_id: int):
        result = (
            supabase.table("notificaciones")
            .select("*")
            .eq("usuario_id", usuario_id)
            .order("creada_en", desc=True)
            .execute()
        )
        return result.data

    def marcar_como_leida(self, notificacion_id: int, usuario_id: int):
        result = (
            supabase.table("notificaciones")
            .update({"leida": True})
            .eq("id", notificacion_id)
            .eq("usuario_id", usuario_id)
            .execute()
        )
        return result.data[0] if result.data else None

    def marcar_todas_como_leidas(self, usuario_id: int):
        supabase.table("notificaciones").update({"leida": True}).eq("usuario_id", usuario_id).eq("leida", False).execute()