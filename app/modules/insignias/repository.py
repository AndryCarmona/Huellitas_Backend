from supabase import Client
from typing import List, Dict, Any
from app.core.database import supabase 

class InsigniaRepository:
    def __init__(self, supabase_client):
        self.supabase = supabase_client

    async def obtener_catalogo_insignias(self) -> List[Dict[str, Any]]:
        """Trae todas las insignias del catálogo."""
        response = self.supabase.table('insignias').select('*').execute()
        return response.data

    async def obtener_insignias_de_usuario(self, usuario_id: int) -> List[Dict[str, Any]]:
        """Trae solo las insignias que el usuario ya ganó."""
        response = (
            self.supabase.table('usuario_insignias')
            .select('insignia_id, fecha_obtencion')
            .eq('usuario_id', usuario_id)
            .execute()
        )
        return response.data