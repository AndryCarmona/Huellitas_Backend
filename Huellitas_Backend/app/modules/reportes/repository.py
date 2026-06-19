from app.core.database import supabase

class ReporteRepository:

    def create(self, data: dict):
        result = supabase.table("reportes").insert(data).execute()
        return result.data[0]