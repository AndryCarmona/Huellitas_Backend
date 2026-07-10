from app.core.database import supabase
from typing import List


class InsigniaRepository:

    def obtener_catalogo_insignias(self) -> List[dict]:
        """Trae todas las insignias del catálogo."""
        response = supabase.table('insignias').select('*').execute()
        return response.data

    def obtener_insignias_por_categoria(self, categoria: str) -> List[dict]:
        """Obtiene todas las insignias de una categoría."""
        response = (
            supabase.table("insignias")
            .select("*")
            .eq("categoria", categoria)
            .execute()
        )
        return response.data

    def obtener_insignias_de_usuario(self, usuario_id: int) -> List[dict]:
        """Obtiene las insignias que el usuario ya tiene."""
        response = (
            supabase.table("usuario_insignias")
            .select("insignia_id, fecha_obtencion")  
            .eq("usuario_id", usuario_id)
            .execute()
        )
        return response.data

    def otorgar_insignia(self, usuario_id: int, insignia_id: int):
        """Otorga una insignia a un usuario."""
        response = (
            supabase.table("usuario_insignias")
            .insert({
                "usuario_id": usuario_id,
                "insignia_id": insignia_id,
                "fecha_obtencion": "now()"
            })
            .execute()
        )
        return response.data