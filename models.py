# models.py - versión unificada y corregida

from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLAlchemyEnum, Text, DateTime
from sqlalchemy.orm import relationship
from database import Base
import enum


# -----------------------------
# ENUMS
# -----------------------------

class UserRole(str, enum.Enum):
    PSICOLOGO = "psicologo"
    PACIENTE = "paciente"


class AppointmentStatus(str, enum.Enum):
    AGENDADA = "agendada"
    COMPLETADA = "completada"
    CANCELADA_PACIENTE = "cancelada_paciente"
    CANCELADA_PSICOLOGO = "cancelada_psicologo"


# -----------------------------
# TABLAS
# -----------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Guardamos el valor del enum (psicologo | paciente)
    role = Column(
        SQLAlchemyEnum(UserRole, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )

    # Relaciones
    profile = relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # Un psicólogo (owner) tiene muchos pacientes
    patients = relationship("Patient", back_populates="owner")

    # Un psicólogo tiene muchas citas
    appointments = relationship("Appointment", back_populates="psychologist")

    # Bloques de disponibilidad del psicólogo
    availability_blocks = relationship(
        "AvailabilityBlock",
        back_populates="psychologist",
        cascade="all, delete-orphan"
    )


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
    nombre = Column(String, index=True, nullable=False)
    edad = Column(Integer, nullable=False)
    dni = Column(String, nullable=True)
    telefono = Column(String, nullable=True)

    # Clave foránea al psicólogo (User) dueño de este paciente
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="patients")

    # Un paciente puede tener muchas citas
    appointments = relationship(
        "Appointment",
        back_populates="patient",
        cascade="all, delete-orphan"
    )


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    # Guardamos el valor del enum (agendada | completada | ...)
    status = Column(
        SQLAlchemyEnum(AppointmentStatus, values_callable=lambda x: [e.value for e in x]),
        default=AppointmentStatus.AGENDADA.value,
        nullable=False
    )

    notes = Column(Text, nullable=True)           # Notas pre o post sesión
    video_call_link = Column(String, nullable=True)

    # Claves foráneas
    psychologist_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)

    # Relaciones inversas
    psychologist = relationship("User", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")


class AvailabilityBlock(Base):
    __tablename__ = "availability_blocks"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    # Clave foránea al psicólogo que define esta disponibilidad
    psychologist_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relación hacia el usuario psicólogo
    psychologist = relationship("User", back_populates="availability_blocks")
