from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from .schemas import UsuarioCreate, UsuarioResponse, UsuarioLogin, Token, EditarPerfilRequest, CambiarContraseniaRequest, ActualizarFotoPerfilRequest, UsuarioPublicoResponse, SolicitarCodigoRequest, ConfirmarCodigoRequest
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
        usuario_credentials.identificador,
        usuario_credentials.contrasenia
    )

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = service.crear_sesion_token(data={"sub": usuario["correo"]})

    usuario_data = {
        "usuario_id_pk": usuario["usuario_id_pk"],
        "correo": usuario["correo"],
        "nombre": usuario["nombre"],
        "apellidos": usuario["apellidos"],
        "nombre_usuario": usuario.get("nombre_usuario"),
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
        "foto_perfil": usuario.get("foto_perfil"),
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

@router.patch("/foto-perfil-catalogo", response_model=UsuarioResponse)
def foto_perfil_catalogo(
    datos: ActualizarFotoPerfilRequest,
    usuario_actual: dict = Depends(get_current_user),
):
    service = UsuarioService()
    try:
        return service.actualizar_foto_perfil_catalogo(
            usuario_actual["usuario_id_pk"], datos.foto_perfil
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/foto-perfil-personalizada", response_model=UsuarioResponse)
def foto_perfil_personalizada(
    file: UploadFile = File(...),
    usuario_actual: dict = Depends(get_current_user),
):
    service = UsuarioService()
    try:
        return service.subir_foto_perfil_personalizada(
            usuario_actual["usuario_id_pk"], file
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/{usuario_id}", response_model=UsuarioPublicoResponse)
def obtener_perfil_publico(
    usuario_id: int,
    usuario_actual: dict = Depends(get_current_user),
):
    service = UsuarioService()
    try:
        return service.obtener_perfil_publico(usuario_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/enviar-codigo")
async def enviar_codigo(datos: SolicitarCodigoRequest):
    service = UsuarioService()
    try:
        return await service.solicitar_codigo_correo(datos.correo)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al enviar código: {str(e)}")


@router.post("/confirmar-codigo")
def confirmar_codigo(datos: ConfirmarCodigoRequest):
    service = UsuarioService()
    try:
        return service.confirmar_codigo_correo(datos.correo, datos.codigo)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))