# models.py - ACTUALIZADO CON CITAS (APPOINTMENTS)

from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLAlchemyEnum, Text, DateTime
from sqlalchemy.orm import relationship
from database import Base 
import enum

# --- ENUMS: Para estandarizar valores ---

class UserRole(str, enum.Enum):
    PSICOLOGO = "psicologo"
    PACIENTE = "paciente"

class AppointmentStatus(str, enum.Enum):
    AGENDADA = "agendada"
    COMPLETADA = "completada"
    CANCELADA_PACIENTE = "cancelada_paciente"
    CANCELADA_PSICOLOGO = "cancelada_psicologo"

# --- TABLAS PRINCIPALES ---

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(SQLAlchemyEnum(UserRole, values_callable=lambda x: [e.value for e in x]), nullable=False)
    
    # RELACIONES
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    # Un psicólogo (owner) tiene muchos pacientes
    patients = relationship("Patient", back_populates="owner")
    
    # Un psicólogo tiene muchas citas
    appointments = relationship("Appointment", back_populates="psychologist")

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String, index=True)
    foto_url = Column(String, nullable=True)
    descripcion = Column(Text, nullable=True)
    numero_licencia = Column(String, nullable=True, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    user = relationship("User", back_populates="profile")

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    edad = Column(Integer)
    dni = Column(String, nullable=True) # DNI puede ser opcional
    telefono = Column(String, nullable=True) # Telefono puede ser opcional
    
    # Clave foránea al psicólogo (User) dueño de este paciente
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="patients")
    
    # Un paciente puede tener muchas citas
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")

# --- NUEVA TABLA DE CITAS (APPOINTMENTS) ---
class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(SQLAlchemyEnum(AppointmentStatus), default=AppointmentStatus.AGENDADA, nullable=False)
    notes = Column(Text, nullable=True) # Notas pre o post sesión
    video_call_link = Column(String, nullable=True) # Para el Módulo 2
    
    # Clave foránea al psicólogo
    psychologist_id = Column(Integer, ForeignKey("users.id"))
    # Clave foránea al paciente
    patient_id = Column(Integer, ForeignKey("patients.id"))

    # Relaciones inversas
    psychologist = relationship("User", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")