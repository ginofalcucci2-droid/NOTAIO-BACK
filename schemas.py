# schemas.py
from pydantic import BaseModel

# Define la estructura de datos que esperamos recibir al crear un usuario.
class UserCreate(BaseModel):
    email: str
    password: str
    role: str

# Define la estructura de datos que devolveremos (NUNCA la contraseña).
class UserResponse(BaseModel):
    id: int
    email: str
    role: str

    class Config:
        from_attributes = True