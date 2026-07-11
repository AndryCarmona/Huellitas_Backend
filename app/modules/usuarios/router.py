from fastapi import APIRouter, HTTPException, status, Depends
from .schemas import UsuarioCreate, UsuarioResponse, UsuarioLogin, Token, EditarPerfilRequest, CambiarContraseniaRequest
from .service import UsuarioService
from fastapi import Depends, Form, File, UploadFile
from app.core.security import get_current_user


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

    usuario_data = {
        "usuario_id_pk": usuario["usuario_id_pk"],
        "correo": usuario["correo"],
        "nombre": usuario["nombre"],
        "apellidos": usuario["apellidos"],
        "num_telefono": usuario["num_telefono"],
        "fecha_nacimiento": usuario["fecha_nacimiento"],
        "verificado": usuario["verificado"],
        "fecha_registro_usuario": usuario["fecha_registro_usuario"],
        "rol_usuario": usuario["rol_usuario"],
        "calle": usuario.get("calle"),
        "colonia": usuario.get("colonia"),
        "cp": usuario.get("cp"),
        "ciudad": usuario.get("ciudad"),
        "estado": usuario.get("estado"),
    }

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": usuario_data
    }

@router.patch("/completar-perfil", response_model=UsuarioResponse)
def completar_perfil(
    calle: str = Form(...),
    colonia: str = Form(...),
    cp: str = Form(...),
    ciudad: str = Form(...),
    estado: str = Form(...),
    identificacion_frontal: UploadFile = File(...),
    identificacion_trasera: UploadFile = File(...),
    selfie: UploadFile = File(...),
    usuario_actual: dict = Depends(get_current_user),
):
    service = UsuarioService()
    try:
        return service.completar_perfil(
            usuario_actual["usuario_id_pk"],
            calle, colonia, cp, ciudad, estado,
            identificacion_frontal, identificacion_trasera, selfie
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al completar perfil: {str(e)}")


@router.patch("/editar-perfil", response_model=UsuarioResponse)
def editar_perfil(
    datos: EditarPerfilRequest,
    usuario_actual: dict = Depends(get_current_user),
):
    service = UsuarioService()
    try:
        return service.editar_perfil(usuario_actual["usuario_id_pk"], datos)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al editar perfil: {str(e)}")

@router.patch("/cambiar-contrasenia")
def cambiar_contrasenia(
    datos: CambiarContraseniaRequest,
    usuario_actual: dict = Depends(get_current_user),
):
    service = UsuarioService()
    try:
        return service.cambiar_contrasenia(
            usuario_actual["usuario_id_pk"],
            datos.contrasenia_actual,
            datos.contrasenia_nueva,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cambiar contraseña: {str(e)}")