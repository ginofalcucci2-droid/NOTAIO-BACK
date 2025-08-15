# routers/patients.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from auth import get_current_user, get_db

# Creamos un router, es como una "mini-app" de FastAPI
router = APIRouter(
    prefix="/patients", # Todos los endpoints aquí empezarán con /patients
    tags=["Patients"],   # Agrupa los endpoints en la documentación de Swagger
    responses={404: {"description": "Not found"}}, # Respuesta por defecto para 404
)

@router.post("/", response_model=schemas.PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(
    patient: schemas.PatientCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    Crea un nuevo paciente. El paciente quedará asociado al psicólogo
    actualmente autenticado.
    """
    # Creamos el objeto del modelo SQLAlchemy asignando el owner_id
    db_patient = models.Patient(**patient.dict(), owner_id=current_user.id)
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

@router.get("/", response_model=List[schemas.PatientResponse])
def read_patients(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Obtiene una lista de todos los pacientes asociados al psicólogo
    actualmente autenticado.
    """
    patients = db.query(models.Patient).filter(models.Patient.owner_id == current_user.id).offset(skip).limit(limit).all()
    return patients

@router.get("/{patient_id}", response_model=schemas.PatientResponse)
def read_patient(
    patient_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Obtiene los detalles de un paciente específico.
    Verifica que el paciente pertenezca al psicólogo autenticado.
    """
    db_patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
        
    if db_patient.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tiene permiso para ver este paciente")
        
    return db_patient

@router.put("/{patient_id}", response_model=schemas.PatientResponse)
def update_patient(
    patient_id: int, 
    patient_update: schemas.PatientUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Actualiza los datos de un paciente específico.
    """
    db_patient = read_patient(patient_id, db, current_user) # Reutilizamos la lógica de permisos
    
    update_data = patient_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_patient, key, value)
        
    db.commit()
    db.refresh(db_patient)
    return db_patient

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Elimina un paciente específico.
    """
    db_patient = read_patient(patient_id, db, current_user) # Reutilizamos la lógica de permisos
    
    db.delete(db_patient)
    db.commit()
    return {"ok": True}