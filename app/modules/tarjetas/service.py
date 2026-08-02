from .repository import TarjetaRepository
from .schemas import TarjetaCreate, TarjetaUpdate
from app.core.security import (encriptar_numero, enmascarar_numero, detectar_tipo_tarjeta,)

class TarjetaService:
    def __init__(self):
        self.repository = TarjetaRepository()

    def obtener_tarjetas_usuario(self, usuario_id: int):
        """Obtiene todas las tarjetas de un usuario."""
        tarjetas = self.repository.obtener_tarjetas_por_usuario(usuario_id)
        return [
            {k: v for k, v in t.items() if k != "numero_encriptado"}
            for t in tarjetas
        ]

    def crear_tarjeta(self, usuario_id: int, data: TarjetaCreate):
        """Crea una nueva tarjeta encriptada."""
        numero_limpio = data.numeroTarjeta.replace(' ', '')

        if len(numero_limpio) < 13 or len(numero_limpio) > 19:
            raise ValueError("Número de tarjeta inválido")

        numero_encriptado = encriptar_numero(numero_limpio)
        numero_enmascarado = enmascarar_numero(numero_limpio)
        
        tipo = data.tipo or detectar_tipo_tarjeta(numero_limpio)

        if data.esPredeterminada:
            self.repository.quitar_predeterminada_de_usuario(usuario_id)

        tarjeta_data = {
            "usuario_id": usuario_id,
            "numero_enmascarado": numero_enmascarado,
            "numero_encriptado": numero_encriptado,
            "titular": data.titular,
            "fecha_vencimiento": data.fechaVencimiento,
            "tipo": tipo,
            "es_predeterminada": data.esPredeterminada,
        }

        nueva_tarjeta = self.repository.crear_tarjeta(tarjeta_data)
        nueva_tarjeta.pop("numero_encriptado", None)
        return nueva_tarjeta

    def actualizar_tarjeta(self, tarjeta_id: int, data: TarjetaUpdate):
        """Actualiza una tarjeta existente."""
        tarjeta = self.repository.obtener_tarjeta_por_id(tarjeta_id)
        if not tarjeta:
            raise ValueError("Tarjeta no encontrada")

        update_data = {}

        if data.titular is not None:
            update_data["titular"] = data.titular
        if data.fechaVencimiento is not None:
            update_data["fecha_vencimiento"] = data.fechaVencimiento

        if data.esPredeterminada is True:
            self.repository.quitar_predeterminada_de_usuario(tarjeta["usuario_id"])
            update_data["es_predeterminada"] = True
        elif data.esPredeterminada is False:
            update_data["es_predeterminada"] = False

        if not update_data:
            return tarjeta

        tarjeta_actualizada = self.repository.actualizar_tarjeta(tarjeta_id, update_data)
        tarjeta_actualizada.pop("numero_encriptado", None)
        return tarjeta_actualizada

    def eliminar_tarjeta(self, tarjeta_id: int):
        """Elimina una tarjeta."""
        tarjeta = self.repository.obtener_tarjeta_por_id(tarjeta_id)
        if not tarjeta:
            raise ValueError("Tarjeta no encontrada")

        eliminada = self.repository.eliminar_tarjeta(tarjeta_id)
        if not eliminada:
            raise ValueError("No se pudo eliminar la tarjeta")
        return True

    def establecer_predeterminada(self, tarjeta_id: int):
        """Establece una tarjeta como predeterminada."""
        tarjeta = self.repository.obtener_tarjeta_por_id(tarjeta_id)
        if not tarjeta:
            raise ValueError("Tarjeta no encontrada")

        self.repository.quitar_predeterminada_de_usuario(tarjeta["usuario_id"])
        self.repository.actualizar_tarjeta(tarjeta_id, {"es_predeterminada": True})
        return {"message": "Tarjeta predeterminada actualizada"}

    def obtener_tarjeta_para_pago(self, tarjeta_id: int) -> dict:
        """Obtiene una tarjeta con su número desencriptado (solo para uso interno)."""
        tarjeta = self.repository.obtener_tarjeta_por_id(tarjeta_id)
        if not tarjeta:
            raise ValueError("Tarjeta no encontrada")

        from app.core.security import desencriptar_numero
        tarjeta["numero_completo"] = desencriptar_numero(tarjeta["numero_encriptado"])
        return tarjeta