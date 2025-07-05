from models.database import engine, SessionLocal
from models.registro import Registro
from utils.auth import get_password_hash
from sqlalchemy import text

def init_db():
    """Inicializar la base de datos"""
    # Crear todas las tablas
    from models.database import Base
    Base.metadata.create_all(bind=engine)
    
    # Crear sesión de base de datos
    db = SessionLocal()
    
    try:
        # Verificar si ya existe un usuario administrador
        admin_user = db.query(User).filter(User.email == "admin@feelguard.com").first()
        
        if not admin_user:
            # Crear usuario administrador
            admin_user = User(
                email="admin@feelguard.com",
                username="admin",
                full_name="Administrador",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_superuser=True
            )
            db.add(admin_user)
            db.commit()
            print("Usuario administrador creado:")
            print("Email: admin@feelguard.com")
            print("Contraseña: admin123")
        
        # Verificar si ya existe un usuario de prueba
        test_user = db.query(User).filter(User.email == "test@feelguard.com").first()
        
        if not test_user:
            # Crear usuario de prueba
            test_user = User(
                email="test@feelguard.com",
                username="testuser",
                full_name="Usuario de Prueba",
                hashed_password=get_password_hash("test123"),
                is_active=True,
                is_superuser=False
            )
            db.add(test_user)
            db.commit()
            print("Usuario de prueba creado:")
            print("Email: test@feelguard.com")
            print("Contraseña: test123")
        
        print("Base de datos inicializada correctamente!")
        
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db() 