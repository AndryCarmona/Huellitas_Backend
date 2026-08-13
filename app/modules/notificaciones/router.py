from fastapi import APIRouter, HTTPException, Depends
from app.core.security import get_current_user
from .service import obtener_notificaciones_usuario, marcar_como_leida, marcar_todas_como_leidas
from .schemas import NotificacionResponse

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])

@router.get("/usuario", response_model=list[NotificacionResponse])
def listar(usuario_actual: dict = Depends(get_current_user)):
    return obtener_notificaciones_usuario(usuario_actual["usuario_id_pk"])

@router.patch("/{notificacion_id}/leida")
def marcar_leida(notificacion_id: int, usuario_actual: dict = Depends(get_current_user)):
    try:
        marcar_como_leida(notificacion_id, usuario_actual["usuario_id_pk"])
        return {"mensaje": "Notificación marcada como leída"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/usuario/leer-todas")
def marcar_todas(usuario_actual: dict = Depends(get_current_user)):
    marcar_todas_como_leidas(usuario_actual["usuario_id_pk"])
    return {"mensaje": "Todas las notificaciones marcadas como leídas"}