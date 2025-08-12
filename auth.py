# auth.py

import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from datetime import datetime, timedelta

class AuthHandler():
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # Estos deberían estar en variables de entorno en un proyecto real
    SECRET_KEY = "MI_CLAVE_SECRETA_SUPER_SECRETA" 
    ALGORITHM = "HS256"
    
    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def encode_token(self, user_id, user_email):
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, hours=1), # El token expira en 1 hora
            'iat': datetime.utcnow(),
            'sub': user_id,
            'email': user_email
        }
        return jwt.encode(
            payload,
            self.SECRET_KEY,
            algorithm=self.ALGORITHM
        )

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='La firma ha expirado')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Token inválido')

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)