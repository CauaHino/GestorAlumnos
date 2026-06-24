from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from fastapi import HTTPException, status
import os

# Cargamos las variables de entorno desde el archivo .env
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Le decimos a passlib que use el algoritmo bcrypt para encriptar
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esto le indica a FastAPI en qué ruta web los usuarios enviarán su email/password
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def obtener_password_hash(password: str):
    return pwd_context.hash(password)

def verificar_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)

def crear_token_acceso(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verificar_token_acceso(token: str):
    """
    Recibe el token JWT, comprueba que no esté manipulado ni caducado, 
    y devuelve el email del usuario.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                detail="Usuario Invalido")
        return email
    
    # 3. Control de errores de seguridad
    except jwt.ExpiredSignatureError:
        # Salta si han pasado los 30 minutos de caducidad
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="El token ha caducado. Por favor, inicia sesión de nuevo."
        )
    except jwt.PyJWTError:
        # Salta si alguien se ha inventado el token o lo ha modificado a mano
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token inválido o credenciales incorrectas."
        )