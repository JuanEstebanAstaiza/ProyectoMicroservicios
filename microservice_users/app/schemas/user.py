from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# --- Esquemas Base ---
class UserBase(BaseModel):
    """Esquema base con campos comunes."""
    email: EmailStr
    full_name: Optional[str] = None

# --- Esquema para Crear Usuario (Entrada API) ---
class UserCreate(UserBase):
    """Esquema para recibir datos al crear un usuario."""
    # Usamos Field para añadir validación extra (longitud mínima)
    password: str = Field(..., min_length=8)

# --- Esquema para Actualizar Usuario (Entrada API) ---
class UserUpdate(BaseModel):
    """Esquema para recibir datos al actualizar (todos opcionales)."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None

# --- Esquema para Leer Usuario (Salida API) ---
# Este esquema se usa para devolver datos desde la API.
# Hereda de UserBase y añade campos específicos para la lectura.
class User(UserBase):
    """Esquema para devolver datos de usuario desde la API."""
    id: int
    is_active: bool

    class Config:
        # Configuración para que Pydantic funcione con modelos ORM (SQLAlchemy)
        from_attributes = True # Anteriormente 'orm_mode = True' en Pydantic V1