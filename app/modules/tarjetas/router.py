from fastapi import APIRouter, HTTPException, Depends
from .service import TarjetaService
from .schemas import TarjetaCreate, TarjetaUpdate, TarjetaResponse
from app.core.security import get_current_user

router = APIRouter(prefix="/tarjetas", tags=["Tarjetas"])
tarjeta_service = TarjetaService()

@router.get("/usuario/mis-tarjetas", response_model=list[TarjetaResponse])
def obtener_mis_tarjetas(current_user: dict = Depends(get_current_user)):
    """Obtiene todas las tarjetas del usuario autenticado."""
    try:
        usuario_id = current_user["usuario_id_pk"]
        return tarjeta_service.obtener_tarjetas_usuario(usuario_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener tarjetas: {str(e)}")

@router.post("/", response_model=TarjetaResponse, status_code=201)
def crear_tarjeta(data: TarjetaCreate, current_user: dict = Depends(get_current_user)):
    """Guarda una nueva tarjeta encriptada."""
    try:
        usuario_id = current_user["usuario_id_pk"]
        return tarjeta_service.crear_tarjeta(usuario_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear tarjeta: {str(e)}")

@router.put("/{tarjeta_id}", response_model=TarjetaResponse)
def actualizar_tarjeta(tarjeta_id: int, data: TarjetaUpdate, current_user: dict = Depends(get_current_user)):
    """Actualiza una tarjeta existente."""
    try:
        tarjeta = tarjeta_service.repository.obtener_tarjeta_por_id(tarjeta_id)
        if not tarjeta:
            raise ValueError("Tarjeta no encontrada")
        
        usuario_id = current_user["usuario_id_pk"]
        if tarjeta["usuario_id"] != usuario_id:
            raise HTTPException(status_code=403, detail="No tienes permiso para modificar esta tarjeta")
        
        return tarjeta_service.actualizar_tarjeta(tarjeta_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar tarjeta: {str(e)}")

@router.delete("/{tarjeta_id}", status_code=204)
def eliminar_tarjeta(tarjeta_id: int, current_user: dict = Depends(get_current_user)):
    """Elimina una tarjeta."""
    try:
        tarjeta = tarjeta_service.repository.obtener_tarjeta_por_id(tarjeta_id)
        if not tarjeta:
            raise ValueError("Tarjeta no encontrada")
        
        usuario_id = current_user["usuario_id_pk"]
        if tarjeta["usuario_id"] != usuario_id:
            raise HTTPException(status_code=403, detail="No tienes permiso para eliminar esta tarjeta")
        
        tarjeta_service.eliminar_tarjeta(tarjeta_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar tarjeta: {str(e)}")

@router.post("/{tarjeta_id}/predeterminada")
def establecer_predeterminada(tarjeta_id: int, current_user: dict = Depends(get_current_user)):
    """Establece una tarjeta como predeterminada."""
    try:
        tarjeta = tarjeta_service.repository.obtener_tarjeta_por_id(tarjeta_id)
        if not tarjeta:
            raise ValueError("Tarjeta no encontrada")
        
        usuario_id = current_user["usuario_id_pk"]
        if tarjeta["usuario_id"] != usuario_id:
            raise HTTPException(status_code=403, detail="No tienes permiso para modificar esta tarjeta")
        
        return tarjeta_service.establecer_predeterminada(tarjeta_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al establecer predeterminada: {str(e)}")