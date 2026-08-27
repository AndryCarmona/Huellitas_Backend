from app.core.database import supabase
from typing import List, Optional, Dict, Any

class DonacionRepository:
    def obtener_todas_las_organizaciones(self) -> List[Dict[str, Any]]:
        """Obtiene todas las organizaciones sin filtrar."""
        response = (supabase.table("organizaciones").select("*").execute())
        return response.data
    
    def obtener_organizaciones_por_categoria(self, categoria: str) -> List[Dict[str, Any]]:
        """Obtiene todas las organizaciones de una categoría específica."""
        response = (supabase.table("organizaciones").select("*").eq("categoria", categoria).execute())
        return response.data

    def obtener_organizacion_por_id(self, organizacion_id: int) -> Optional[Dict[str, Any]]:
        """Verifica si una organización existe por su ID."""
        response = (supabase.table("organizaciones").select("*").eq("id", organizacion_id).execute())
        return response.data[0] if response.data else None

    def obtener_tarjeta_por_id(self, tarjeta_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una tarjeta por su ID (solo datos básicos para validación)."""
        response = (supabase.table("tarjetas_usuario").select("tarjeta_id, usuario_id").eq("tarjeta_id", tarjeta_id).execute())
        return response.data[0] if response.data else None

    #def crear_donacion(self, donacion_data: Dict[str, Any]) -> Dict[str, Any]:
    #    """Inserta una nueva donación en la base de datos."""
    #    response = (supabase.table("donaciones").insert(donacion_data).execute())
    #    return response.data[0]

    def contar_donaciones_usuario(self, usuario_id: int) -> int:
        """Cuenta el total de donaciones completadas de un usuario."""
        response = (supabase.table("donaciones").select("id", count="exact").eq("usuario_id", usuario_id).eq("estado", "completada").execute())
        return response.count if response.count else 0
    def obtener_donaciones_por_usuario(self, usuario_id: int) -> List[Dict[str, Any]]:
        """Obtiene todas las donaciones de un usuario, ordenadas por fecha (más reciente primero)."""
        response = (
            supabase.table("donaciones")
            .select("*")
            .eq("usuario_id", usuario_id)
            .order("fecha_donacion", desc=True)
            .execute()
        )
        return response.data

    def obtener_donaciones_recibidas(self, organizacion_id: int, limite: int = 50) -> List[Dict[str, Any]]:
        """Obtiene las donaciones completadas de una organización, ordenadas por fecha."""
        response = (
            supabase.table("donaciones")
            .select("*")
            .eq("organizacion_id", organizacion_id)
            .eq("estado", "completada")
            .order("fecha_donacion", desc=True)
            .limit(limite)
            .execute()
        )
        return response.data or []

    def actualizar_meta_mensual(self, organizacion_id: int, nueva_meta: float) -> Dict[str, Any]:
        """Actualiza la meta mensual de la organización."""
        response = (
            supabase.table("organizaciones")
            .update({"meta_mensual": nueva_meta})
            .eq("id", organizacion_id) # Ajusta a tu PK real si es organizacion_id_pk
            .execute()
        )
        return response.data[0] if response.data else {}