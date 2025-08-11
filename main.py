# main.py - VERSIÓN CON CORS

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Importamos la herramienta de CORS

app = FastAPI()

# --- CONFIGURACIÓN DE CORS ---
# Le decimos al backend que permita peticiones desde nuestro frontend de React.
origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"], # Permite todas las cabeceras
)

# --- DATOS DE EJEMPLO ---
patients_data = [
    { "id": 1, "nombre": 'Mocho Monteros', "edad": 28, "dni": 'S/D', "telefono": 'S/D' },
    { "id": 2, "nombre": 'Tano Falcone', "edad": 29, "dni": '39730806', "telefono": '3814634400' },
    { "id": 3, "nombre": 'Pepito Juarez', "edad": 29, "dni": 'S/D', "telefono": 'S/D' },
]

# --- ENDPOINTS DE LA API ---
@app.get("/")
def read_root():
    return {"message": "¡Bienvenido al backend de Notaio!"}

@app.get("/patients")
def get_patients():
    return patients_data    