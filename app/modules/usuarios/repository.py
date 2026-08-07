from app.core.database import supabase

class UsuarioRepository:
    
    def obtener_correo(self, correo: str):
        result = supabase.table("usuario").select("*").eq("correo", correo).execute()
        return result.data[0] if result.data else None
    
    def crear_usuario(self, data: dict):
        result = supabase.table("usuario").insert(data).execute()
        return result.data[0]
    
    def obtener_por_id(self, usuario_id: int):
        result = supabase.table("usuario").select("*").eq("usuario_id_pk", usuario_id).execute()
        return result.data[0] if result.data else None

    def actualizar_perfil(self, usuario_id: int, data: dict):
        result = supabase.table("usuario").update(data).eq("usuario_id_pk", usuario_id).execute()
        return result.data[0] if result.data else None
    
    def obtener_por_nombre_usuario(self, nombre_usuario: str):
        result = supabase.table("usuario").select("*").eq("nombre_usuario", nombre_usuario).execute()
        return result.data[0] if result.data else None

# --- Verificación de correo (pre-registro) ---

    def obtener_verificacion(self, correo: str):
        result = supabase.table("verificacion_correo").select("*").eq("correo", correo).execute()
        return result.data[0] if result.data else None

    def guardar_codigo_verificacion(self, correo: str, codigo: str, expira_en: str):
        result = supabase.table("verificacion_correo").upsert(
            {"correo": correo, "codigo": codigo, "expira_en": expira_en, "confirmado": False},
            on_conflict="correo"
        ).execute()
        return result.data[0]

    def confirmar_verificacion(self, correo: str):
        result = supabase.table("verificacion_correo").update(
            {"confirmado": True}
        ).eq("correo", correo).execute()
        return result.data[0] if result.data else None

    def eliminar_verificacion(self, correo: str):
        supabase.table("verificacion_correo").delete().eq("correo", correo).execute()