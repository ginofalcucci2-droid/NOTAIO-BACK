# main.py - ACTUALIZADO PARA INCLUIR EL ROUTER DE PACIENTES
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import models
import database
import schemas
from auth import auth_handler, get_current_user, get_db
from routers import patients, availability
from routers import patients

# Crea las tablas en la base de datos si no existen
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Notaio API",
    description="El backend para la plataforma de psicología Notaio."
)

# --- CONFIGURACIÓN DE CORS ---
origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- INCLUIMOS EL ROUTER DE PACIENTES ---
app.include_router(patients.router)
app.include_router(availability.router)


# --- Endpoints Públicos y de Autenticación (sin cambios) ---
@app.get("/psychologists", response_model=List[schemas.PsychologistPublicProfile], tags=["Marketplace"])
def get_all_psychologists(db: Session = Depends(get_db)):
    """
    Devuelve una lista de perfiles públicos de todos los usuarios
    que tienen el rol de 'psicologo'.
    """
    # 1. Buscamos todos los usuarios que son psicólogos
    psychologist_users = db.query(models.User).filter(models.User.role == models.UserRole.PSICOLOGO).all()
    
    # 2. Extraemos sus perfiles (asegurándonos de que no sean nulos)
    profiles = [user.profile for user in psychologist_users if user.profile is not None]
    
    return profiles

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "¡Bienvenido al backend de Notaio!"}

# ... (el resto de tu código de /register, /token, y /users/me/profile se mantiene igual)
# ... (asegúrate de pegar el resto de tus funciones aquí)
# ...
# En main.py

@app.post("/register", response_model=schemas.UserResponse, tags=["Authentication"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    
    # --- ESPÍA #1: ¿QUÉ LLEGÓ EXACTAMENTE? ---
    print("=============================================")
    print(f"PASO 1: Datos recibidos por el endpoint: {user.dict()}")
    print("=============================================")

    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    hashed_password = auth_handler.get_password_hash(user.password)
    
    if user.role not in [e.value for e in models.UserRole]:
        raise HTTPException(status_code=400, detail=f"Rol '{user.role}' inválido.")

    # --- ESPÍA #2: ¿QUÉ ROL VAMOS A USAR? ---
    try:
        user_role_enum = models.UserRole(user.role)
        print(f"PASO 2: El string '{user.role}' se convirtió exitosamente al Enum: {user_role_enum}")
    except Exception as e:
        print(f"ERROR EN PASO 2: Falló la conversión del rol. Error: {e}")
        raise HTTPException(status_code=400, detail="Error interno al procesar el rol.")

    # --- ESPÍA #3: ¿QUÉ VAMOS A GUARDAR EN LA BASE DE DATOS? ---
    new_user = models.User(
        email=user.email, 
        hashed_password=hashed_password, 
        role=user_role_enum
    )
    print(f"PASO 3: Objeto 'User' a punto de ser guardado:")
    print(f"  - Email: {new_user.email}")
    print(f"  - Rol: {new_user.role} (Tipo: {type(new_user.role)})")
    print("=============================================")

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # --- ESPÍA #4: ¿QUÉ SE GUARDÓ REALMENTE? ---
    print(f"PASO 4: Usuario guardado en la BBDD. ID: {new_user.id}, Rol guardado: {new_user.role}")
    print("=============================================")

    # Creamos el perfil asociado
    new_profile = models.Profile(
        nombre_completo=user.full_name,
        user_id=new_user.id
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.post('/token', tags=['Authentication'])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    if not user or not auth_handler.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Email o contraseña incorrectos',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    
    token = auth_handler.encode_token(user_id=user.id, user_email=user.email)
    return {'access_token': token, 'token_type': 'bearer'}

# --- Endpoints de Perfil de Usuario ---

@app.get("/users/me", response_model=schemas.UserDetailsResponse, tags=["User Profile"])
def read_current_user_details(current_user: models.User = Depends(get_current_user)):
    """
    Obtiene los detalles completos del usuario autenticado, incluyendo su perfil.
    """
    return current_user


@app.put("/users/me/profile", response_model=schemas.ProfileResponse, tags=["User Profile"])
def update_user_profile(
    profile_update: schemas.ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Crea o actualiza el perfil del usuario autenticado.
    """
    # Si el usuario ya tiene un perfil, lo actualizamos
    if current_user.profile:
        update_data = profile_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(current_user.profile, key, value)
        
        db.commit()
        db.refresh(current_user.profile)
        return current_user.profile
    
    # Si no tiene perfil, creamos uno nuevo
    else:
        # Aquí, ProfileCreate asegura que al menos se provea 'nombre_completo'
        # pero como nuestro ProfileUpdate es más flexible, adaptamos los datos.
        new_profile_data = profile_update.dict(exclude_unset=True)
        if not new_profile_data.get("nombre_completo"):
            raise HTTPException(status_code=422, detail="El campo 'nombre_completo' es obligatorio para crear un perfil.")

        new_profile = models.Profile(**new_profile_data, user_id=current_user.id)
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)
        return new_profile