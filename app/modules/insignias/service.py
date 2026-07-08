from typing import List
from .repository import InsigniaRepository
from .schemas import InsigniaResponse

class InsigniaService:
    def __init__(self, repository: InsigniaRepository):
        self.repository = repository

    async def obtener_insignias_usuario(self, usuario_id_pk: int) -> List[InsigniaResponse]:
        # 1. Pedimos los datos al repositorio
        catalogo = await self.repository.obtener_catalogo_insignias()
        obtenidas = await self.repository.obtener_insignias_de_usuario(usuario_id_pk)

        # 2. Procesamos los datos (Lógica de negocio)
        mapa_obtenidas = {item['insignia_id']: item['fecha_obtencion'] for item in obtenidas}

        resultado = []
        for ins in catalogo:
            resultado.append(
                InsigniaResponse(
                    id=ins['id_insignias'],
                    nombre=ins['nombre'],
                    nivel=ins['nivel'],
                    categoria=ins['categoria'],
                    descripcion=ins['descripcion'],
                    imagen_url=ins.get('imagen_url'),
                    obtenida=ins['id_insignias'] in mapa_obtenidas,
                    fecha_obtencion=mapa_obtenidas.get(ins['id_insignias'])
                )
            )
        
        return resultado