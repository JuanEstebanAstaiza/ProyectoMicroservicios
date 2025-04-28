from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- URL Hardcodeada ---
# ¡ADVERTENCIA! Esto no es recomendable para producción.
# Reemplaza con los datos reales de tu conexión a PostgreSQL.
# Si usas Docker Compose/K8s, el host será el nombre del servicio de la BD.
# Ejemplo para desarrollo local: "postgresql://user:password@localhost:5432/users_db"
# Ejemplo para Docker Compose (si el servicio se llama 'db_users'): "postgresql://user:password@db_users:5432/users_db"
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost:5432/users_db"
# ----------------------

# Crear el motor SQLAlchemy
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Crear una fábrica de sesiones (SessionLocal)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear una clase base para nuestros modelos ORM
Base = declarative_base()

def get_db():
    """
    Generador de dependencias para obtener una sesión de base de datos.
    Asegura que la sesión se cierre después de cada solicitud.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()