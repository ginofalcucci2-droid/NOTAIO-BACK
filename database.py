# database.py - CONFIGURADO PARA SUPABASE

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

# 1. Cargar las variables de entorno desde el archivo .env
load_dotenv()

# 2. Obtener la URL de la base de datos desde las variables de entorno
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")


# --- Verificación Crucial ---
if not SQLALCHEMY_DATABASE_URL:
    raise Exception(
        "No se encontró la variable de entorno DATABASE_URL. "
        "Asegúrate de que el archivo .env exista en el directorio raíz "
        "y contenga la variable DATABASE_URL."
    )

# 3. Crear el "motor" de SQLAlchemy, ahora sin los argumentos específicos de SQLite
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 4. Configurar la fábrica de sesiones (esto no cambia)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. Centralizar la Base declarativa para que los modelos la importen desde aquí
Base = declarative_base()