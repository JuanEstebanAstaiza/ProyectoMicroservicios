from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- URL Hardcodeada ---
# ¡ADVERTENCIA! No es recomendable para producción.
# Usa el nombre del servicio definido en docker-compose.yml o Kubernetes
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgres-db:5432/users_db"
#                                           ^^^^^^^^^^^ (Nombre del servicio de la BD Postgres)
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