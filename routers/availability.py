# routers/availability.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import models
import schemas
from auth import get_current_user, get_db

router = APIRouter(
    prefix="/availability",
    tags=["Availability"],
)

# --- Endpoints para que el Psicólogo gestione su disponibilidad ---

@router.post("/blocks", response_model=schemas.AvailabilityBlockResponse, status_code=status.HTTP_201_CREATED)
def create_availability_block(
    block: schemas.AvailabilityBlockCreate,
    db: Session = Depends(get_d b),
    current_user: models.User = Depends(get_current_user)
):
    """
    Permite a un psicólogo (autenticado) crear un nuevo bloque
    de tiempo en el que está disponible.
    """
    if current_user.role != models.UserRole.PSICOLOGO:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo los psicólogos pueden definir su disponibilidad")

    # TODO: Añadir validación para que start_time sea anterior a end_time
    
    db_block = models.AvailabilityBlock(
        **block.dict(), 
        psychologist_id=current_user.id
    )
    db.add(db_block)
    db.commit()
    db.refresh(db_block)
    return db_block

@router.get("/my-blocks", response_model=List[schemas.AvailabilityBlockResponse])
def get_my_availability_blocks(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Obtiene los bloques de disponibilidad del psicólogo autenticado
    dentro de un rango de fechas.
    """
    blocks = db.query(models.AvailabilityBlock).filter(
        models.AvailabilityBlock.psychologist_id == current_user.id,
        models.AvailabilityBlock.start_time >= start_date,
        models.AvailabilityBlock.end_time <= end_date
    ).all()
    return blocks

@router.delete("/blocks/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_availability_block(
    block_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Permite a un psicólogo eliminar uno de sus bloques de disponibilidad.
    """
    db_block = db.query(models.AvailabilityBlock).filter(models.AvailabilityBlock.id == block_id).first()

    if not db_block:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bloque no encontrado")

    if db_block.psychologist_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tiene permiso para eliminar este bloque")

    db.delete(db_block)
    db.commit()
    return

# --- Endpoint público para que los Pacientes vean la disponibilidad ---

@router.get("/psychologist/{psychologist_id}", response_model=List[schemas.AvailabilityBlockResponse])
def get_psychologist_availability(
    psychologist_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db)
):
    """
    Endpoint PÚBLICO para que cualquier usuario (ej. un paciente) vea
    los bloques de disponibilidad de un psicólogo específico en un rango de fechas.
    """
    # TODO: En un futuro, aquí cruzaremos esta info con las citas ya agendadas
    # para mostrar solo los huecos realmente libres.
    
    blocks = db.query(models.AvailabilityBlock).filter(
        models.AvailabilityBlock.psychologist_id == psychologist_id,
        models.AvailabilityBlock.start_time >= start_date,
        models.AvailabilityBlock.end_time <= end_date
    ).all()
    return blocks