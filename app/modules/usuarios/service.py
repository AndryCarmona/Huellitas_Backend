from app.core.database import SUPABASE_JWT
import jwt 
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext 
from .repository import UsuarioRepository
from .schemas import UsuarioCreate, EditarPerfilRequest
from app.core.database import supabase

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
BUCKET_NAME = "usuarios-completar-perfil"
BUCKET_FOTOS_PERFIL = "fotos-perfil"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UsuarioService:
    def __init__(self):
        self.repository = UsuarioRepository()
    
    def crear_sesion_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, SUPABASE_JWT, algorithm=ALGORITHM)
        return encoded_jwt
    
    def registrar_usuario(self, usuario_data: UsuarioCreate):
        existing_usuario = self.repository.obtener_correo(usuario_data.correo)
        if existing_usuario:
            raise ValueError("El correo ya está registrado")

        existing_username = self.repository.obtener_por_nombre_usuario(usuario_data.nombre_usuario)
        if existing_username:
            raise ValueError("El nombre de usuario ya está en uso")

        contrasenia = pwd_context.hash(usuario_data.contrasenia)

        payload = {
            "correo": usuario_data.correo,
            "contrasenia": contrasenia,
            "nombre": usuario_data.nombre,
            "apellidos": usuario_data.apellidos,
            "nombre_usuario": usuario_data.nombre_usuario,
            "num_telefono": usuario_data.num_telefono,
            "fecha_nacimiento": usuario_data.fecha_nacimiento.isoformat(),
            "calle": usuario_data.calle,
            "colonia": usuario_data.colonia,
            "cp": usuario_data.cp,
            "ciudad": usuario_data.ciudad,
            "identificacion_frontal": usuario_data.identificacion_frontal,
            "identificacion_trasera": usuario_data.identificacion_trasera,
            "verificado": False,
            "rol_usuario": "usuario",
        }

        return self.repository.crear_usuario(payload)

    def iniciar_sesion(self, identificador: str, password: str):
        if "@" in identificador:
            usuario = self.repository.obtener_correo(identificador)
        else:
            usuario = self.repository.obtener_por_nombre_usuario(identificador)

        if not usuario:
            return None

        if not pwd_context.verify(password, usuario["contrasenia"]):
            return None

        return usuario
    
    # Completar_perfil
    def _subir_foto(self, usuario_id: int, archivo, tipo: str) -> str:
        contenido = archivo.file.read()
        extension = archivo.filename.split(".")[-1]
        ruta = f"{usuario_id}/{tipo}.{extension}"
        supabase.storage.from_(BUCKET_NAME).upload(
            ruta, contenido, {"content-type": archivo.content_type, "upsert": "true"}
        )
        return supabase.storage.from_(BUCKET_NAME).get_public_url(ruta)

    def completar_perfil(self, usuario_id, calle, colonia, cp, ciudad, estado, frontal, trasera, selfie):
        usuario = self.repository.obtener_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        url_frontal = self._subir_foto(usuario_id, frontal, "frontal")
        url_trasera = self._subir_foto(usuario_id, trasera, "trasera")
        url_selfie = self._subir_foto(usuario_id, selfie, "selfie")

        data = {
            "calle": calle,
            "colonia": colonia,
            "cp": cp,
            "ciudad": ciudad,
            "estado": estado,
            "identificacion_frontal": url_frontal,
            "identificacion_trasera": url_trasera,
            "foto_selfie": url_selfie,
            "verificado": True,
            "rol_usuario": "usuario_verificado",
        }
        return self.repository.actualizar_perfil(usuario_id, data)

    #Actualizar info del perfil
    def editar_perfil(self, usuario_id: int, datos: EditarPerfilRequest):
        usuario = self.repository.obtener_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        data = {k: v for k, v in datos.dict().items() if v is not None}

        if not data:
            raise ValueError("No se enviaron campos para actualizar")

        if "nombre_usuario" in data:
            existente = self.repository.obtener_por_nombre_usuario(data["nombre_usuario"])
            if existente and existente["usuario_id_pk"] != usuario_id:
                raise ValueError("El nombre de usuario ya está en uso")

        return self.repository.actualizar_perfil(usuario_id, data)

    def cambiar_contrasenia(self, usuario_id: int, contrasenia_actual: str, contrasenia_nueva: str):
        usuario = self.repository.obtener_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        if not pwd_context.verify(contrasenia_actual, usuario["contrasenia"]):
            raise ValueError("La contraseña actual es incorrecta")

        nueva_hasheada = pwd_context.hash(contrasenia_nueva)
        self.repository.actualizar_perfil(usuario_id, {"contrasenia": nueva_hasheada})

        return {"mensaje": "Contraseña actualizada correctamente"}

    def actualizar_foto_perfil_catalogo(self, usuario_id: int, nombre_avatar: str):
        usuario = self.repository.obtener_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        return self.repository.actualizar_perfil(usuario_id, {"foto_perfil": nombre_avatar})

    def subir_foto_perfil_personalizada(self, usuario_id: int, archivo):
        usuario = self.repository.obtener_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        contenido = archivo.file.read()
        extension = archivo.filename.split(".")[-1]
        ruta = f"{usuario_id}/perfil.{extension}"

        supabase.storage.from_(BUCKET_FOTOS_PERFIL).upload(
            ruta, contenido, {"content-type": archivo.content_type, "upsert": "true"}
        )
        url = supabase.storage.from_(BUCKET_FOTOS_PERFIL).get_public_url(ruta)

        return self.repository.actualizar_perfil(usuario_id, {"foto_perfil": url})