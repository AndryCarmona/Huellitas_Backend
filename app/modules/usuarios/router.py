#RUTAS DE LA API
from fastapi import APIRouter, HTTPException, status
from app.main import supabase  # Asegúrate de que apunte a donde instanciaste tu cliente de Supabase
from .schemas import RegistroUsuarioRequest

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)

@router.post("/registro")
def registrar_usuario(datos: RegistroUsuarioRequest):
    try:
        # Probemos SOLO el paso de Auth
        auth_response = supabase.auth.sign_up({
            "email": datos.email,
            "password": datos.password
        })
        
        return {"mensaje": "¡El paso de Auth funcionó perfectamente!", "id": auth_response.user.id}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en Auth: {str(e)}")