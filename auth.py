# auth.py - VERSIÓN FINAL Y CORRECTA PARA GESTIÓN DE PERFILES

import jwt
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import models
import database

# --- Dependencias Reutilizables ---

def get_db():
    """
    Dependencia de FastAPI para obtener una sesión de base de datos.
    """
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Clase de Autenticación ---

class AuthHandler():
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # Estos deberían estar en variables de entorno
    SECRET_KEY = "MI_CLAVE_SECRETA_SUPER_SECRETA" 
    ALGORITHM = "HS256"
    
    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def encode_token(self, user_id, user_email):
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, hours=1),
            'iat': datetime.utcnow(),
            'sub': str(user_id), # Es buena práctica asegurar que 'sub' sea un string
            'email': user_email
        }
        return jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='La firma ha expirado')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Token inválido')

# --- Dependencia Principal de Usuario Autenticado ---

auth_handler = AuthHandler() # Creamos una instancia global para usar en la dependencia

def get_current_user(token: str = Depends(auth_handler.security), db: Session = Depends(get_db)):
    """
    Decodifica el token, obtiene el ID del usuario, busca al usuario en la BD
    y devuelve el objeto completo del usuario.
    """
    try:
        payload = auth_handler.decode_token(token.credentials)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido, 'sub' no encontrado")
        
        user = db.query(models.User).filter(models.User.id == int(user_id)).first()
        
        if user is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return user
    except (jwt.PyJWTError, ValueError):
         # Captura errores de decodificación o si 'sub' no es un entero válido
        raise HTTPException(
            status_code=401,
            detail="No se pudo validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )