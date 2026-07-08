from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.core.database import supabase

from .schemas import InsigniaResponse
from .repository import InsigniaRepository
from .service import InsigniaService

router = APIRouter(prefix="/insignias", tags=["Insignias"])

def get_insignia_service() -> InsigniaService:
    repo = InsigniaRepository(supabase)
    return InsigniaService(repo)

@router.get("/usuario/{usuario_id}", response_model=List[InsigniaResponse])
async def obtener_insignias_usuario(
    usuario_id: int, 
    service: InsigniaService = Depends(get_insignia_service)
):
    try:
        return await service.obtener_insignias_usuario(usuario_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")