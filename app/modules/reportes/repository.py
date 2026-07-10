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

    def obtener_estado_reporte(self, reporte_id: int):
        """Obtiene el estado actual del reporte con su historial."""
        reporte_response = supabase.table("reporte").select("""
            reporte_id,
            urgencia_id,
            tipo_reporte,
            descripcion,
            ubicacion,
            tipo_animal,
            raza_id,
            tamano,
            evidencia,
            fase_actual_id
        """).eq("reporte_id", reporte_id).execute()

        if not reporte_response.data:
            raise ValueError("Reporte no encontrado")

        reporte = reporte_response.data[0]

        historial_response = supabase.table("historial_fases_reporte").select("""
            fase_reporte(nombre),
            fecha_cambio,
            evidencia_url
        """).eq("reporte_id", reporte_id).order("fecha_cambio", desc=True).execute()

        historial_str = [
            f"{h['fase_reporte']['nombre']} - {h['fecha_cambio']}"
            for h in historial_response.data
        ]

        return {
            "reporteId": reporte["reporte_id"],
            "faseActual": reporte.get("fase_actual_id", 1),
            "nivelUrgencia": str(reporte["urgencia_id"]),  # ← Corregido
            "tipoReporte": str(reporte["tipo_reporte"]),
            "descripcion": reporte["descripcion"],
            "ubicacion": reporte["ubicacion"],
            "tipoAnimal": str(reporte["tipo_animal"]),
            "raza": reporte["raza_id"],
            "tamano": reporte["tamano"],
            "evidenciaUrl": reporte["evidencia"],
            "historialFases": historial_str
        }

    def actualizar_estado_reporte(self, reporte_id: int, nueva_fase_id: int, evidencia_url: str, comentarios: str = None):
        """Actualiza la fase actual del reporte y guarda en el historial."""
        #Actualizar la fase actual
        supabase.table("reporte").update({
            "fase_actual_id": nueva_fase_id,
            "evidencia": evidencia_url
        }).eq("reporte_id", reporte_id).execute()

        # 2. Insertar en el historial
        supabase.table("historial_fases_reporte").insert({
            "reporte_id": reporte_id,
            "fase_id": nueva_fase_id,
            "evidencia_url": evidencia_url,
            "usuario_id": usuario_id,
            "comentarios": comentarios
        }).execute()

        return True