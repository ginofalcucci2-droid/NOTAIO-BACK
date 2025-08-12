# create_db.py
from database import engine
import models

print("Creando la base de datos y las tablas...")
models.Base.metadata.create_all(bind=engine)
print("¡Base de datos y tablas creadas con éxito!")