# schemas.py - VERSIÓN LIMPIA Y ORGANIZADA

from pydantic import BaseModel
from typing import Optional

# --- Schemas para el Usuario ---

class UserCreate(BaseModel):
    email: str
    password: str
    role: str

class UserResponse(BaseModel):
    id: int
    email: str
    role: str

    class Config:
        from_attributes = True

# --- Schemas para el Perfil ---

class ProfileBase(BaseModel):
    nombre_completo: Optional[str] = None
    foto_url: Optional[str] = None
    descripcion: Optional[str] = None
    numero_licencia: Optional[str] = None

class ProfileCreate(ProfileBase):
    nombre_completo: str

class ProfileUpdate(ProfileBase):
    pass

class ProfileResponse(ProfileBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True