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
            fase_actual_id,
            usuario_rescate_id
        """).eq("reporte_id", reporte_id).execute()

        if not reporte_response.data:
            raise ValueError("Reporte no encontrado")

        reporte = reporte_response.data[0]

        usuario_rescate_nombre = None
        if reporte.get("usuario_rescate_id"):
            usuario_response = (
                supabase.table("usuario")
                .select("nombre")
                .eq("usuario_id_pk", reporte["usuario_rescate_id"])
                .execute()
            )
            if usuario_response.data:
                usuario_rescate_nombre = usuario_response.data[0]["nombre"]

        historial_response = supabase.table("historial_fases_reporte").select("""
            fase_reporte(nombre),
            fecha_cambio,
            evidencia_url,
            comentarios,
            usuario:usuario_id(nombre)
        """).eq("reporte_id", reporte_id).order("fecha_cambio", desc=True).execute()

        historial_str = [
            {
                "fase_nombre": h["fase_reporte"]["nombre"],
                "fecha_cambio": h["fecha_cambio"],
                "evidencia_url": h["evidencia_url"],
                "comentarios": h.get("comentarios"),
                "usuario_nombre": h.get("usuario", {}).get("nombre") if h.get("usuario") else None
            }
            for h in historial_response.data
        ]

        comentarios_str = None
        if historial_str and len(historial_str)> 0:
            comentarios_str=historial_str[0]["comentarios"]

        return {
            "reporteId": reporte["reporte_id"],
            "faseActual": reporte.get("fase_actual_id", 1),
            "nivelUrgencia": str(reporte["urgencia_id"]),
            "tipoReporte": str(reporte["tipo_reporte"]),
            "descripcion": reporte["descripcion"],
            "ubicacion": reporte["ubicacion"],
            "tipoAnimal": str(reporte["tipo_animal"]),
            "raza": reporte["raza_id"],
            "tamano": reporte["tamano"],
            "evidenciaUrl": reporte["evidencia"],
            "usuarioRescateId": reporte.get("usuario_rescate_id"),
            "usuarioRescateNombre": usuario_rescate_nombre,
            "historialFases": historial_str,
            "comentarios":comentarios_str
        }

    def actualizar_estado_reporte(self, reporte_id: int, nueva_fase_id: int, evidencia_url: str, usuario_id: int = None, comentarios: str = None):
        """Actualiza la fase actual del reporte y guarda en el historial."""
        #self.validar_usuario_asignado(reporte_id, usuario_id)
        
        supabase.table("reporte").update({
            "fase_actual_id": nueva_fase_id,
            "evidencia": evidencia_url
        }).eq("reporte_id", reporte_id).execute()

        data_historial = {
        "reporte_id": reporte_id,
        "fase_id": nueva_fase_id,
        "evidencia_url": evidencia_url,
        "comentarios": comentarios
        }
    
        if usuario_id is not None:
            data_historial["usuario_id"] = usuario_id

        # 3. Insertar en el historial
        supabase.table("historial_fases_reporte").insert(data_historial).execute()

        return True
    
    def tomar_reporte(self, reporte_id: int, usuario_id: int):
        """Asigna al usuario actual como responsable del rescate, si nadie lo tiene ya."""
        response = (
            supabase.table("reporte")
            .select("usuario_rescate_id")
            .eq("reporte_id", reporte_id)
            .execute()
        )
        if not response.data:
            raise ValueError("Reporte no encontrado")

        asignado_actual = response.data[0].get("usuario_rescate_id")

        if asignado_actual is not None and asignado_actual != usuario_id:
            usuario_response = (
                supabase.table("usuario")
                .select("nombre")
                .eq("usuario_id_pk", asignado_actual)
                .execute()
            )
            nombre = usuario_response.data[0]["nombre"] if usuario_response.data else "otro usuario"
            raise PermissionError(f"Este reporte ya está siendo atendido por {nombre}")

        supabase.table("reporte").update({
            "usuario_rescate_id": usuario_id
        }).eq("reporte_id", reporte_id).execute()

        return True

    def validar_usuario_asignado(self, reporte_id: int, usuario_id: int):
        """Verifica que el usuario que intenta actualizar el estado sea quien tomó el reporte."""
        response = (
            supabase.table("reporte")
            .select("usuario_rescate_id")
            .eq("reporte_id", reporte_id)
            .execute()
        )
        if not response.data:
            raise ValueError("Reporte no encontrado")

        asignado = response.data[0].get("usuario_rescate_id")

        if asignado is None:
            raise PermissionError("Debes tomar el reporte antes de actualizar su estado")
        if asignado != usuario_id:
            usuario_response = (
                supabase.table("usuario")
                .select("nombre")
                .eq("usuario_id_pk", asignado)
                .execute()
            )
            nombre = usuario_response.data[0]["nombre"] if usuario_response.data else "otro usuario"
            raise PermissionError(f"No estás autorizado. Este reporte lo está atendiendo {nombre}")