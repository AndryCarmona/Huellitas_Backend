from fastapi import APIRouter, HTTPException, status
from .schemas import UsuarioCreate, UsuarioResponse, UsuarioLogin, Token
from .service import UsuarioService

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar(usuario: UsuarioCreate):
    service = UsuarioService()
    try:
        new_usuario = service.registrar_usuario(usuario)
        return new_usuario
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear usuario: {str(e)}"
        )
@router.post("/login")
def login(usuario_credentials: UsuarioLogin):
    service = UsuarioService()
    usuario = service.iniciar_sesion(
        usuario_credentials.correo, 
        usuario_credentials.contrasenia
    )
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = service.crear_sesion_token(data={"sub": usuario["correo"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "nombre": usuario.get("nombre", "Usuario") 
        }
    }