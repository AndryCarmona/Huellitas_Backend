from datetime import datetime, timezone
from app.core.database import supabase
from .schemas import DonacionCreate
from .repository import DonacionRepository
from app.modules.insignias.repository import InsigniaRepository

# Instancia del repositorio de insignias
insignia_repo = InsigniaRepository()

# Umbrales de insignias por nivel
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
        
        # 1. Validar que la organización exista
        organizacion = self.repository.obtener_organizacion_por_id(data.organizacionId)
        if not organizacion:
            raise ValueError("Organización no encontrada")

        # 2. Preparar datos para Supabase
        payload = {
            "usuario_id": data.usuarioId,
            "organizacion_id": data.organizacionId,
            "monto": data.monto,
            "numero_tarjeta": data.numeroTarjeta,
            "titular_tarjeta": data.titularTarjeta,
            "cvv": data.cvv,
            "fecha_vencimiento": data.fechaVencimiento,
            "fecha_donacion": "now()",
            "estado": "completada"
        }

        print("PAYLOAD A INSERTAR:", payload)

        # 3. Guardar en Supabase
        response = supabase.table("donaciones").insert(payload).execute()
        
        # 4. Verificar insignias por donación
        self._verificar_insignias_donaciones(data.usuarioId)

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