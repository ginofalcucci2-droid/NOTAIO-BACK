# main.py - VERSIÓN CON INDENTACIÓN CORREGIDA

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import models
import database
import schemas
from auth import AuthHandler

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# --- CONFIGURACIÓN DE CORS ---
origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

auth_handler = AuthHandler()

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

@app.post("/register", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    hashed_password = auth_handler.get_password_hash(user.password)
    
    from models import UserRole
    try:
        user_role_enum = UserRole[user.role.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Rol '{user.role}' inválido.")

    new_user = models.User(email=user.email, hashed_password=hashed_password, role=user_role_enum)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post('/token', tags=['authentication'])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    if not user or not auth_handler.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Email o contraseña incorrectos',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    
    token = auth_handler.encode_token(user.id, user.email)
    return {'access_token': token, 'token_type': 'bearer'}

@app.get('/protected', tags=['test'])
def protected_route(user_info: dict = Depends(auth_handler.auth_wrapper)):
    return {'message': '¡Has accedido a una ruta protegida!', 'user': user_info}

@app.get("/patients")
def get_patients(db: Session = Depends(get_db)):
    patients = db.query(models.Patient).all()
    return patients