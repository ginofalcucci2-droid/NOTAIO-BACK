# create_db.py

# Importamos las herramientas necesarias
from database import engine
import models

print("Creando la base de datos y las tablas...")

# Esta es la misma línea que teníamos antes, pero en su propio script
models.Base.metadata.create_all(bind=engine)

print("¡Base de datos y tablas creadas con éxito!")