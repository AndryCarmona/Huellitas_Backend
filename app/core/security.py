from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import jwt
from jwt.exceptions import PyJWTError
from app.core.database import SUPABASE_JWT
from app.modules.usuarios.repository import UsuarioRepository

ALGORITHM = "HS256"
bearer_scheme = HTTPBearer()

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