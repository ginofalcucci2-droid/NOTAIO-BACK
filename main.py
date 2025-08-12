# main.py - Versión con Endpoint de Login

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # Un helper para formularios de login
from sqlalchemy.orm import Session
import models
import database
import schemas
import security
from auth import AuthHandler # ¡Importamos nuestra nueva herramienta!

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
auth_handler = AuthHandler() # Creamos una instancia de nuestro manejador de auth

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

# ¡NUEVO ENDPOINT DE LOGIN!
@app.post('/token', tags=['authentication'])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. Buscamos al usuario por su email (en el formulario de login, el 'username' es nuestro email)
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    # 2. Si no existe el usuario o la contraseña es incorrecta, devolvemos un error
    if not user or not auth_handler.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Email o contraseña incorrectos',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    
    # 3. Si todo es correcto, creamos y devolvemos el token
    token = auth_handler.encode_token(user.id, user.email)
    return {'access_token': token, 'token_type': 'bearer'}


# Ejemplo de RUTA PROTEGIDA
@app.get('/protected', tags=['test'])
def protected_route(user_info: dict = Depends(auth_handler.auth_wrapper)):
    # Gracias a 'Depends', esta ruta solo funcionará si el frontend envía un token válido.
    # 'user_info' contendrá los datos decodificados del token.
    return {'message': '¡Has accedido a una ruta protegida!', 'user': user_info}


@app.get("/patients")
def get_patients(db: Session = Depends(get_db)):
    patients = db.query(models.Patient).all()
    return patients