from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from microservice_users.app.db.database import Base

class User(Base):
    """Modelo ORM para la tabla de usuarios."""
    __tablename__ = "users" # Nombre de la tabla en la base de datos

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True)
    is_active = Column(Boolean, default=True)

    # Aquí podrías definir relaciones si tuvieras otras tablas
    # ej. items = relationship("Item", back_populates="owner")