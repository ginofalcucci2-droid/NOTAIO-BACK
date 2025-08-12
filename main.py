# main.py - Versión con conexión a BD

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import models
import database
# Esta línea ahora está en database.py, pero la dejamos aquí por si acaso
# para asegurar que las tablas se creen al arrancar.
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# --- Función de Dependencia ---
# Esto nos dará una sesión de BD para cada petición de la API
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

# Endpoint modificado para usar la base de datos
@app.get("/patients")
def get_patients(db: Session = Depends(get_db)):
    # Consulta la tabla de pacientes y devuelve todos los resultados
    patients = db.query(models.Patient).all()
    return patients