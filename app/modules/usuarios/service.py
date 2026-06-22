from app.core.database import SUPABASE_JWT
import jwt 
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext 
from .repository import UsuarioRepository
from .schemas import UsuarioCreate

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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
        
        contrasenia = pwd_context.hash(usuario_data.contrasenia)
        
        payload = {
            "correo": usuario_data.correo,
            "contrasenia": contrasenia,
            "nombre": usuario_data.nombre,
            "apellidos": usuario_data.apellidos,
            "num_telefono": usuario_data.num_telefono,
            "fecha_nacimiento": usuario_data.fecha_nacimiento.isoformat(),
            "calle": usuario_data.calle,
            "colonia": usuario_data.colonia,
            "cp": usuario_data.cp,
            "ciudad": usuario_data.ciudad,
            "identificacion_frontal": usuario_data.identificacion_frontal,
            "identificacion_trasera": usuario_data.identificacion_trasera,
            "verificado": False,
            "rol_usuario": "usuario"
        }
        
        return self.repository.crear_usuario(payload)
    
    def iniciar_sesion(self, correo: str, password: str):
        usuario = self.repository.obtener_correo(correo)
        if not usuario:
            return None
        
        if not pwd_context.verify(password, usuario["contrasenia"]):
            return None
            
        return usuario