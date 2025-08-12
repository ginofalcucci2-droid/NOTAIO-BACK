# models.py - VERSIÓN MULTIUSUARIO

from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from .database import Base
import enum

# Definimos los roles que puede tener un usuario
class UserRole(enum.Enum):
    PSICOLOGO = "psicologo"
    PACIENTE = "paciente"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    # NUEVO CAMPO: Para saber si el usuario es psicólogo o paciente
    role = Column(SQLAlchemyEnum(UserRole), nullable=False)
    
    # Relación: Un psicólogo (User con rol 'psicologo') tiene muchos pacientes (Patient)
    patients = relationship("Patient", back_populates="owner")

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    edad = Column(Integer)
    dni = Column(String)
    telefono = Column(String)
    
    # Esta columna nos dice qué psicólogo es el "dueño" de este paciente
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="patients")