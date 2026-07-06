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