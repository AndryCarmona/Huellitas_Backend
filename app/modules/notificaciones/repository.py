from app.core.database import supabase

class NotificacionRepository:
    def crear_notificaciones(self, notificaciones: list[dict]):
        if not notificaciones:
            return []
        result = supabase.table("notificaciones").insert(notificaciones).execute()
        return result.data