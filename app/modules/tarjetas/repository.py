from app.core.database import supabase
from typing import List, Optional, Dict, Any


class TarjetaRepository:

    def obtener_tarjetas_por_usuario(self, usuario_id: int) -> List[Dict[str, Any]]:
        """Obtiene todas las tarjetas de un usuario (solo datos enmascarados)."""
        response = (
            supabase.table("tarjetas_usuario")
            .select("*")
            .eq("usuario_id", usuario_id)
            .order("es_predeterminada", desc=True)
            .order("fecha_creacion", desc=True)
            .execute()
        )
        return response.data

    def obtener_tarjeta_por_id(self, tarjeta_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una tarjeta por su ID."""
        response = (
            supabase.table("tarjetas_usuario")
            .select("*")
            .eq("tarjeta_id", tarjeta_id)
            .execute()
        )
        return response.data[0] if response.data else None

    def crear_tarjeta(self, tarjeta_data: Dict[str, Any]) -> Dict[str, Any]:
        """Inserta una nueva tarjeta en la base de datos."""
        response = (
            supabase.table("tarjetas_usuario")
            .insert(tarjeta_data)
            .execute()
        )
        return response.data[0]

    def actualizar_tarjeta(self, tarjeta_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza los datos de una tarjeta."""
        response = (
            supabase.table("tarjetas_usuario")
            .update(update_data)
            .eq("tarjeta_id", tarjeta_id) 
            .execute()
        )
        return response.data[0] if response.data else None

    def eliminar_tarjeta(self, tarjeta_id: int) -> bool:
        """Elimina una tarjeta."""
        response = (
            supabase.table("tarjetas_usuario")
            .delete()
            .eq("tarjeta_id", tarjeta_id)
            .execute()
        )
        return len(response.data) > 0

    def quitar_predeterminada_de_usuario(self, usuario_id: int):
        """Quita el flag de predeterminada de todas las tarjetas de un usuario."""
        supabase.table("tarjetas_usuario") \
            .update({"es_predeterminada": False}) \
            .eq("usuario_id", usuario_id) \
            .execute()