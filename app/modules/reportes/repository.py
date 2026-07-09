from app.core.database import supabase

class ReporteRepository:

    def create(self, data: dict):
        result = supabase.table("reporte").insert(data).execute()
        return result.data[0]

    def contar_reportes_usuario(self, usuario_id: int) -> int:
        """Cuenta cuántos reportes ha hecho un usuario."""
        response = (
            supabase.table("reporte")
            .select("reporte_id", count="exact")
            .eq("usuario_id_fk", usuario_id)
            .execute()
        )
        return response.count