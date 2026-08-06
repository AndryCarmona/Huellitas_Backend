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