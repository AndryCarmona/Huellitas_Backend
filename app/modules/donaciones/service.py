from datetime import datetime, timezone
from app.core.database import supabase
from .schemas import DonacionCreate
from .repository import DonacionRepository
from app.modules.insignias.repository import InsigniaRepository
from app.modules.notificaciones.repository import NotificacionRepository
from typing import Dict, Any, List

notificacion_repo = NotificacionRepository()

#Repos
insignia_repo = InsigniaRepository()

# Umbrales de insignias
UMBRAL_NIVEL = {
    1: 1,    # Nivel 1: 1 donación
    2: 3,    # Nivel 2: 3 donaciones
    3: 5,    # Nivel 3: 5 donaciones
    4: 10,   # Nivel 4: 10 donaciones
    5: 25,   # Nivel 5: 25 donaciones
    6: 50,   # Nivel 6: 50 donaciones
    7: 100   # Nivel 7: 100 donaciones
}

class DonacionService:
    
    def __init__(self):
        self.repository = DonacionRepository()

    def obtener_todas_las_organizaciones(self):
        """Obtiene todas las organizaciones sin filtrar por categoría."""
        return self.repository.obtener_todas_las_organizaciones()

    def obtener_organizaciones_por_categoria(self, categoria: str):
        """Obtiene todas las organizaciones de una categoría específica."""
        return self.repository.obtener_organizaciones_por_categoria(categoria)

    def crear_donacion(self, data: DonacionCreate):
        """Crea una nueva donación y verifica insignias."""
        
        organizacion = self.repository.obtener_organizacion_por_id(data.organizacionId)
        if not organizacion:
            raise ValueError("Organización no encontrada")

        tarjeta = self.repository.obtener_tarjeta_por_id(data.tarjetaId)
        if not tarjeta:
            raise ValueError("Tarjeta no encontrada")
        if tarjeta["usuario_id"] != data.usuarioId:
            raise ValueError("La tarjeta no pertenece al usuario")

        payload = {
            "usuario_id": data.usuarioId,
            "organizacion_id": data.organizacionId,
            "monto": data.monto,
            "tarjeta_id": data.tarjetaId,
            "metodo_pago": data.metodoPago,
            "fecha_donacion": "now()",
            "estado": "completada"
        }

        response = supabase.table("donaciones").insert(payload).execute()
        
        self._verificar_insignias_donaciones(data.usuarioId)
        self._notificar_donacion(data.usuarioId, data.monto, organizacion["nombre"])

        return response.data

    def _verificar_insignias_donaciones(self, usuario_id: int):
        """Cuenta cuántas donaciones completó el usuario y otorga insignias."""
        
        total_donaciones = self.repository.contar_donaciones_usuario(usuario_id)
        print(f"Usuario {usuario_id} tiene {total_donaciones} donaciones")

        insignias_donacion = insignia_repo.obtener_insignias_por_categoria("donacion")
        insignias_ya_obtenidas = insignia_repo.obtener_insignias_de_usuario(usuario_id)
        
        ids_ya_obtenidas = {ins["insignia_id"] for ins in insignias_ya_obtenidas}

        for insignia in insignias_donacion:
            insignia_id = insignia["id_insignias"]
            nivel = insignia["nivel"]

            if insignia_id in ids_ya_obtenidas:
                continue

            umbral = UMBRAL_NIVEL.get(nivel, 999)
            if total_donaciones >= umbral:
                insignia_repo.otorgar_insignia(usuario_id, insignia_id)
                print(f"¡Usuario {usuario_id} obtuvo la insignia: {insignia['nombre']}!")

    def obtener_donaciones_usuario(self, usuario_id: int):
        """Obtiene el historial de donaciones de un usuario."""
        return self.repository.obtener_donaciones_por_usuario(usuario_id)

    def _notificar_donacion(self, usuario_id: int, monto: float, organizacion_nombre: str):
        try:
            notificacion_repo.crear_notificaciones([{
                "usuario_id": usuario_id,
                "tipo": "donacion",
                "titulo": "Gracias por tu donación",
                "mensaje": f"Tu donación de ${monto:.2f} fue procesada exitosamente.",
                "data": {"monto": monto, "organizacion": organizacion_nombre},
            }])
        except Exception as e:
            print(f"No se pudo crear notificación de donación: {e}")

    def obtener_estadisticas_organizacion(self, organizacion_id: int) -> Dict[str, Any]:
        """Obtiene meta, recaudado y listado de donaciones con nombres de donantes."""
        from app.modules.foro.repository import OrganizacionForoRepository
        
        org_repo = OrganizacionForoRepository()
        org = org_repo.obtener_organizacion_por_dueno(0)
        
        meta_mensual = float(org.get("meta_mensual", 0.0)) if org else 0.0
        
        recaudado_mensual = org_repo.obtener_recaudado_mensual(organizacion_id)
        
        donaciones_db = self.repository.obtener_donaciones_recibidas(organizacion_id)
        donaciones_enriquecidas = []
        
        for don in donaciones_db:
            usuario = supabase.table("usuario").select("nombre").eq(
                "usuario_id_pk", don.get("usuario_id")
            ).execute()
            nombre_donante = usuario.data[0]["nombre"] if usuario.data else "Donante Anónimo"
            
            donaciones_enriquecidas.append({
                "id": don["id"],
                "nombre_donante": nombre_donante,
                "fecha_donacion": don["fecha_donacion"],
                "monto": float(don["monto"]),
                "estado": don["estado"]
            })
            
        return {
            "meta_mensual": meta_mensual,
            "recaudado_mensual": recaudado_mensual,
            "donaciones_recientes": donaciones_enriquecidas
        }

    def actualizar_meta_organizacion(self, organizacion_id: int, nueva_meta: float) -> Dict[str, Any]:
        if nueva_meta <= 0:
            raise ValueError("La meta debe ser mayor a 0")
        return self.repository.actualizar_meta_mensual(organizacion_id, nueva_meta)