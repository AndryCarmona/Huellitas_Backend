from .repository import NotificacionRepository

notificacion_repo = NotificacionRepository()

def obtener_notificaciones_usuario(usuario_id: int):
    return notificacion_repo.obtener_por_usuario(usuario_id)

def marcar_como_leida(notificacion_id: int, usuario_id: int):
    resultado = notificacion_repo.marcar_como_leida(notificacion_id, usuario_id)
    if not resultado:
        raise ValueError("Notificación no encontrada")
    return resultado

def marcar_todas_como_leidas(usuario_id: int):
    notificacion_repo.marcar_todas_como_leidas(usuario_id)