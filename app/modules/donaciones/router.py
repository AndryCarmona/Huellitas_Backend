from fastapi import APIRouter, HTTPException, Query, Depends
from .service import DonacionService
from .schemas import DonacionCreate, OrganizacionResponse, DonacionResponse
from app.core.security import get_current_user

router = APIRouter(prefix="/donaciones", tags=["Donaciones"])

donacion_service = DonacionService()

@router.get("/organizaciones", response_model=list[OrganizacionResponse])
def obtener_todas_las_organizaciones():
    """Obtiene todas las organizaciones sin filtrar."""
    try:
        organizaciones = donacion_service.obtener_todas_las_organizaciones()
        return organizaciones
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener organizaciones: {str(e)}")

@router.get("/organizaciones/categoria", response_model=list[OrganizacionResponse])
def obtener_organizaciones_por_categoria(
    categoria: str = Query(..., description="Categoría: sinFinesLucro, refugios, gubernamentales")
):
    """Obtiene organizaciones filtradas por categoría."""
    try:
        organizaciones = donacion_service.obtener_organizaciones_por_categoria(categoria)
        return organizaciones
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener organizaciones: {str(e)}")

@router.post("/", status_code=201)
def crear_donacion(donacion: DonacionCreate):
    try:
        nueva_donacion = donacion_service.crear_donacion(donacion)
        return nueva_donacion
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la donación: {str(e)}")
    
@router.get("/usuario/mis-donaciones")
def obtener_mis_donaciones(current_user: dict = Depends(get_current_user)):
    """Obtiene el historial de donaciones del usuario"""
    try:
        print("CURRENT_USER:", current_user)  # temporal: para ver las claves reales
        usuario_id = (
            current_user.get("usuario_id_pk")
            or current_user.get("usuario_id")
            or current_user.get("id")
        )
        if not usuario_id:
            raise HTTPException(status_code=401, detail="Usuario no identificado")

        donaciones = donacion_service.obtener_donaciones_usuario(usuario_id)
        return donaciones
    except HTTPException:
        raise
    except Exception as e:
        print("ERROR MIS DONACIONES:", e)
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener donaciones: {str(e)}",
        )