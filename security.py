# security.py
from passlib.context import CryptContext

# Configura el contexto para el hashing de contraseñas.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Función para verificar una contraseña.
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Función para "hashear" una contraseña.
def get_password_hash(password):
    return pwd_context.hash(password)