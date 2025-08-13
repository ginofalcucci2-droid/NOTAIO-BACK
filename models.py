# models.py - ACTUALIZADO CON PERFILES

from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLAlchemyEnum, Text
from sqlalchemy.orm import relationship
from database import Base 
import enum

class UserRole(str, enum.Enum):
    PSICOLOGO = "psicologo"
    PACIENTE = "paciente"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(SQLAlchemyEnum(UserRole, values_callable=lambda x: [e.value for e in x]), nullable=False)
    
    # RELACIONES
    patients = relationship("Patient", back_populates="owner")
    
    # --- NUEVA RELACIÓN UNO A UNO CON PROFILE ---
    # `back_populates` apunta a la relación en el modelo Profile.
    # `cascade="all, delete-orphan"` significa que si se borra un usuario, su perfil también se borra.
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")

# --- NUEVA TABLA DE PERFILES ---
class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    
    # Campos comunes para ambos roles
    nombre_completo = Column(String, index=True)
    foto_url = Column(String, nullable=True) # Una foto es opcional
    descripcion = Column(Text, nullable=True) # Usamos Text para descripciones largas
    
    # Campo específico para Psicólogos (opcional)
    numero_licencia = Column(String, nullable=True, unique=True)
    
    # Clave foránea para la relación uno a uno
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # --- RELACIÓN INVERSA CON USER ---
    user = relationship("User", back_populates="profile")


class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    edad = Column(Integer)
    dni = Column(String)
    telefono = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="patients")