# main.py - VERSIÓN FINAL REVISADA

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import database
import schemas
import security

# YA NO creamos las tablas aquí. Eso lo hace 'create_db.py'.

app = FastAPI()

# --- Función de Dependencia para la Sesión de BD ---
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Endpoints de la API ---

@app.get("/")
def read_root():
    return {"message": "¡Bienvenido al backend de Notaio!"}

# ¡NUEVO ENDPOINT DE REGISTRO! - Con la lógica correcta
@app.post("/register", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    hashed_password = security.get_password_hash(user.password)

    # Lógica simple: Pasamos el string del rol directamente.
    # SQLAlchemy ahora sabe cómo manejarlo gracias a la corrección en models.py.
    new_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        role=user.role 
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

# Dentro de main.py

@app.get("/patients")
def get_patients(db: Session = Depends(get_db)):
    patients = db.query(models.Patient).all()
    return patients