# models.py - VERSIÓN FINAL Y CORRECTA (DE VERDAD)

from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class UserRole(str, enum.Enum): # Heredamos de 'str' para mejor compatibilidad
    PSICOLOGO = "psicologo"
    PACIENTE = "paciente"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # ¡AQUÍ ESTÁ EL CAMBIO CLAVE!
    # Le decimos a SQLAlchemy que los valores válidos son los strings "psicologo" y "paciente".
    role = Column(SQLAlchemyEnum(UserRole, values_callable=lambda x: [e.value for e in x]), nullable=False)
    
    patients = relationship("Patient", back_populates="owner")

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    edad = Column(Integer)
    dni = Column(String)
    telefono = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="patients")