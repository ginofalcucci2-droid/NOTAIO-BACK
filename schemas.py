# schemas.py - ACTUALIZADO CON PACIENTES Y CITAS

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import models # Importamos models para poder usar el Enum

# --- Schemas Base ---

class PatientBase(BaseModel):
    nombre: str
    edad: Optional[int] = None
    dni: Optional[str] = None
    telefono: Optional[str] = None

class AppointmentBase(BaseModel):
    start_time: datetime
    end_time: datetime
    notes: Optional[str] = None

# --- Schemas para Creación (lo que recibe la API) ---

class PatientCreate(PatientBase):
    pass

class AppointmentCreate(AppointmentBase):
    patient_id: int

# --- Schemas para Actualización (lo que recibe la API en un PUT/PATCH) ---

class PatientUpdate(PatientBase):
    # Todos los campos son opcionales en la actualización
    nombre: Optional[str] = None

class AppointmentUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[models.AppointmentStatus] = None # Usamos el Enum para validar
    notes: Optional[str] = None

# --- Schemas de Respuesta (lo que devuelve la API) ---

class PatientResponse(PatientBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class AppointmentResponse(AppointmentBase):
    id: int
    status: models.AppointmentStatus
    psychologist_id: int
    patient: PatientResponse # Anidamos la info del paciente en la respuesta

    class Config:
        from_attributes = True

# --- Schemas de Usuario y Perfil (ya existentes, los mantenemos) ---

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