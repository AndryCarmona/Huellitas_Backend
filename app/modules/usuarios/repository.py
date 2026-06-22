from app.core.database import supabase

class UsuarioRepository:
    
    def obtener_correo(self, correo: str):
        result = supabase.table("usuario").select("*").eq("correo", correo).execute()
        return result.data[0] if result.data else None
    
    def crear_usuario(self, data: dict):
        result = supabase.table("usuario").insert(data).execute()
        return result.data[0]