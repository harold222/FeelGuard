import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("DATABASE_URL no está configurada en el entorno.")
    exit(1)

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1 as test"))
        print("Conexión exitosa a la base de datos Supabase!")
        for row in result:
            print("Resultado de prueba:", row)
except Exception as e:
    print("Error al conectar a la base de datos:")
    print(e) 