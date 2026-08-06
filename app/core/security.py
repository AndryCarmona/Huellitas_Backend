from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from cryptography.fernet import Fernet

import os
import jwt
from jwt.exceptions import PyJWTError
from app.core.database import SUPABASE_JWT
from app.modules.usuarios.repository import UsuarioRepository

ALGORITHM = "HS256"
bearer_scheme = HTTPBearer()
CIPHER_KEY = os.getenv('TARJETAS_KEY')
cipher = Fernet(CIPHER_KEY.encode() if isinstance(CIPHER_KEY, str) else CIPHER_KEY)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SUPABASE_JWT, algorithms=[ALGORITHM])
        correo: str = payload.get("sub")
        if correo is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception

    usuario = UsuarioRepository().obtener_correo(correo)
    if usuario is None:
        raise credentials_exception
    return usuario

def encriptar_numero(numero: str) -> str:
    """Encripta el número de tarjeta completo."""
    return cipher.encrypt(numero.encode()).decode()

def desencriptar_numero(numero_encriptado: str) -> str:
    """Desencripta el número para procesar el pago."""
    return cipher.decrypt(numero_encriptado.encode()).decode()

def enmascarar_numero(numero: str) -> str:
    """Convierte num de tarjeta"""
    numero_limpio = numero.replace(' ', '')
    if len(numero_limpio) < 4:
        return '****'
    ultimos_4 = numero_limpio[-4:]
    return f'************{ultimos_4}'

def detectar_tipo_tarjeta(numero: str) -> str:
    """Detecta el tipo de tarjeta basado en el primer dígito."""
    numero_limpio = numero.replace(' ', '')
    if numero_limpio.startswith('4'):
        return 'visa'
    elif numero_limpio.startswith('5') or numero_limpio.startswith('2'):
        return 'mastercard'
    elif numero_limpio.startswith('3'):
        return 'amex'
    return 'otro'