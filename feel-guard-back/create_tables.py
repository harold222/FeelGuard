import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from models.database import Base
import models.registro
from models.chat_history import ChatHistory

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("DATABASE_URL no está configurada en el entorno.")
    exit(1)

try:
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    print("¡Tablas creadas exitosamente en la base de datos!")
except Exception as e:
    print("Error al crear las tablas:")
    print(e) 