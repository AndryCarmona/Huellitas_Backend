from app.core.database import supabase
from datetime import datetime, timedelta, timezone

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

# --- ubicación del usuario ---
    def obtener_usuarios_con_ubicacion_reciente(self, minutos: int = 60):
        limite = (datetime.now(timezone.utc) - timedelta(minutes=minutos)).isoformat()
        result = (
            supabase.table("usuario")
            .select("usuario_id_pk, latitud_actual, longitud_actual")
            .not_.is_("latitud_actual", "null")
            .gte("ubicacion_actualizada_en", limite)
            .execute()
        )
        return result.data

# --- Organización ---
    def crear_organizacion(self, usuario_id: int, data: dict):
        organizacion_data = {
            "nombre": data.get("nombre"),
            "registro_legal": data.get("registro_legal"),
            "categoria": data.get("categoria"),
            "tipos_animales": data.get("tipos_animales"),
            "telefono_emergencia": data.get("telefono_emergencia"),
            "correo_institucional": data.get("correo_institucional"),
            "fecha_fundacion": data.get("fecha_fundacion"),
            "cuenta_bancaria": data.get("cuenta_bancaria"),
            "descripcion": data.get("descripcion"),
            "logo_url": data.get("logo_url"),
            "dueño_id": usuario_id,
        }
        result = supabase.table("organizaciones").insert(organizacion_data).execute()
        return result.data[0] if result.data else None

    def obtener_organizacion_por_dueno(self, usuario_id: int):
        result = supabase.table("organizaciones").select("*").eq("dueño_id", usuario_id).execute()
        return result.data[0] if result.data else None

    def actualizar_organizacion(self, organizacion_id: int, data: dict):
        result = supabase.table("organizaciones").update(data).eq("id", organizacion_id).execute()
        return result.data[0] if result.data else None

    def actualizar_imagenes_organizacion(self, organizacion_id: int, data: dict):
        result = supabase.table("organizaciones").update(data).eq("id", organizacion_id).execute()
        return result.data[0] if result.data else None