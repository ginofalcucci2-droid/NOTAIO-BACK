import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"

sys.path.append(str(Path(__file__).resolve().parents[1]))

import models
import database
import schemas
from main import get_psychologist_public_profile
from routers import session_requests


@pytest.fixture(scope="function")
def session_factory(tmp_path):
    test_db_path = tmp_path / "test.db"
    database_url = f"sqlite:///{test_db_path}"
    os.environ["DATABASE_URL"] = database_url

    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    database.engine = engine
    database.SessionLocal = TestingSessionLocal

    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)

    yield TestingSessionLocal

    models.Base.metadata.drop_all(bind=engine)
    engine.dispose()


def create_psychologist(session):
    psychologist = models.User(
        email="psy@example.com",
        hashed_password="hashed",
        role=models.UserRole.PSICOLOGO.value,
    )
    session.add(psychologist)
    session.commit()
    session.refresh(psychologist)

    profile = models.Profile(
        nombre_completo="Dra. Ana",
        descripcion="Psicóloga especializada en terapia cognitivo conductual",
        tarifa=6000,
        user_id=psychologist.id,
    )
    session.add(profile)
    session.commit()

    availability = models.AvailabilityBlock(
        psychologist_id=psychologist.id,
        start_time=datetime(2024, 1, 1, 15, 0, 0),
        end_time=datetime(2024, 1, 1, 18, 0, 0),
    )
    session.add(availability)
    session.commit()

    return psychologist


def create_patient(session):
    patient = models.User(
        email="patient@example.com",
        hashed_password="hashed",
        role=models.UserRole.PACIENTE.value,
    )
    session.add(patient)
    session.commit()
    session.refresh(patient)
    return patient


def test_get_psychologist_profile_includes_tarifa_and_availability(session_factory):
    SessionLocal = session_factory
    session = SessionLocal()
    try:
        psychologist = create_psychologist(session)
        profile = get_psychologist_public_profile(psychologist.id, db=session)
    finally:
        session.close()

    assert profile.user_id == psychologist.id
    assert profile.tarifa == 6000
    assert len(profile.availability) == 1
    assert profile.availability[0].start_time == datetime(2024, 1, 1, 15, 0, 0)

    with pytest.raises(HTTPException):
        session = SessionLocal()
        try:
            get_psychologist_public_profile(9999, db=session)
        finally:
            session.close()


def test_patient_request_and_psychologist_accept_flow(session_factory):
    SessionLocal = session_factory
    session = SessionLocal()
    try:
        psychologist = create_psychologist(session)
        patient = create_patient(session)

        request_payload = schemas.SessionRequestCreate(
            psychologist_id=psychologist.id,
            start_time=datetime(2024, 1, 1, 16, 0, 0),
            end_time=datetime(2024, 1, 1, 17, 0, 0),
            notes="Sesión introductoria",
        )

        session_request = session_requests.create_session_request(
            request_payload, db=session, current_user=patient
        )
        assert session_request.status == models.SessionRequestStatus.PENDIENTE.value

        accepted_request = session_requests.accept_session_request(
            session_request.id, db=session, current_user=psychologist
        )
        assert accepted_request.status == models.SessionRequestStatus.ACEPTADA.value

        with pytest.raises(HTTPException):
            session_requests.reject_session_request(
                session_request.id, db=session, current_user=psychologist
            )
    finally:
        session.close()
