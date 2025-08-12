# main.py - VERSIÓN FINAL Y CORRECTA

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import models
import database


app = FastAPI()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "¡Bienvenido al backend de Notaio!"}

@app.get("/patients")
def get_patients(db: Session = Depends(get_db)):
    patients = db.query(models.Patient).all()
    return patients