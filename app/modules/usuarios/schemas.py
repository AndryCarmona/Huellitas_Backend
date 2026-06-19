from pydantic import BaseModel, EmailStr
from datetime import date

class RegistroUsuarioRequest(BaseModel):
    email: EmailStr        # Valida que sea un formato de correo real
    password: str         # La contraseña para Supabase Auth
    nombre: str
    apellidos: str
    num_telefono: str
    fecha_nacimiento: date # Valida formato AAAA-MM-DD (ej: "2000-05-15")