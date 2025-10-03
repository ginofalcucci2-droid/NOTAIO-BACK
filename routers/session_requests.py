"""Endpoints para gestionar solicitudes de sesión entre pacientes y psicólogos."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from auth import get_current_user, get_db

router = APIRouter(
    prefix="/session-requests",
    tags=["Session Requests"],
)


def _ensure_time_window_is_valid(start_time, end_time):
    if start_time >= end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La hora de inicio debe ser anterior a la hora de fin",
        )


@router.post("/", response_model=schemas.SessionRequestResponse, status_code=status.HTTP_201_CREATED)
def create_session_request(
    request: schemas.SessionRequestCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Permite a un paciente solicitar una sesión con un psicólogo."""

    if current_user.role != models.UserRole.PACIENTE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los pacientes pueden solicitar sesiones",
        )

    psychologist = (
        db.query(models.User)
        .filter(models.User.id == request.psychologist_id)
        .first()
    )
    if not psychologist or psychologist.role != models.UserRole.PSICOLOGO:
        raise HTTPException(status_code=404, detail="Psicólogo no encontrado")

    _ensure_time_window_is_valid(request.start_time, request.end_time)

    block = (
        db.query(models.AvailabilityBlock)
        .filter(
            models.AvailabilityBlock.psychologist_id == psychologist.id,
            models.AvailabilityBlock.start_time <= request.start_time,
            models.AvailabilityBlock.end_time >= request.end_time,
        )
        .first()
    )
    if not block:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El psicólogo no tiene disponibilidad para ese horario",
        )

    session_request = models.SessionRequest(
        psychologist_id=psychologist.id,
        patient_id=current_user.id,
        start_time=request.start_time,
        end_time=request.end_time,
        notes=request.notes,
        status=models.SessionRequestStatus.PENDIENTE.value,
    )

    db.add(session_request)
    db.commit()
    db.refresh(session_request)

    return session_request


@router.get("/outgoing", response_model=List[schemas.SessionRequestResponse])
def list_outgoing_session_requests(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Lista las solicitudes creadas por el paciente autenticado."""

    if current_user.role != models.UserRole.PACIENTE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los pacientes pueden consultar sus solicitudes",
        )

    requests = (
        db.query(models.SessionRequest)
        .filter(models.SessionRequest.patient_id == current_user.id)
        .order_by(models.SessionRequest.start_time.asc())
        .all()
    )
    return requests


@router.get("/incoming", response_model=List[schemas.SessionRequestResponse])
def list_incoming_session_requests(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Lista las solicitudes que debe responder el psicólogo autenticado."""

    if current_user.role != models.UserRole.PSICOLOGO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los psicólogos pueden revisar solicitudes entrantes",
        )

    requests = (
        db.query(models.SessionRequest)
        .filter(models.SessionRequest.psychologist_id == current_user.id)
        .order_by(models.SessionRequest.start_time.asc())
        .all()
    )
    return requests


@router.post("/{request_id}/accept", response_model=schemas.SessionRequestResponse)
def accept_session_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Permite a un psicólogo aceptar una solicitud de sesión pendiente."""

    if current_user.role != models.UserRole.PSICOLOGO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los psicólogos pueden aceptar solicitudes",
        )

    session_request = (
        db.query(models.SessionRequest)
        .filter(models.SessionRequest.id == request_id)
        .first()
    )
    if not session_request:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    if session_request.psychologist_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para modificar esta solicitud",
        )

    if session_request.status != models.SessionRequestStatus.PENDIENTE.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La solicitud ya fue respondida",
        )

    session_request.status = models.SessionRequestStatus.ACEPTADA.value
    db.commit()
    db.refresh(session_request)
    return session_request


@router.post("/{request_id}/reject", response_model=schemas.SessionRequestResponse)
def reject_session_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Permite a un psicólogo rechazar una solicitud de sesión pendiente."""

    if current_user.role != models.UserRole.PSICOLOGO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los psicólogos pueden rechazar solicitudes",
        )

    session_request = (
        db.query(models.SessionRequest)
        .filter(models.SessionRequest.id == request_id)
        .first()
    )
    if not session_request:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    if session_request.psychologist_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para modificar esta solicitud",
        )

    if session_request.status != models.SessionRequestStatus.PENDIENTE.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La solicitud ya fue respondida",
        )

    session_request.status = models.SessionRequestStatus.RECHAZADA.value
    db.commit()
    db.refresh(session_request)
    return session_request
