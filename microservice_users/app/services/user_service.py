from sqlalchemy.orm import Session
from typing import Optional, List # Importa Optional y List (si también usas List[...])
from microservice_users.app.models.user import User as UserModel # Renombrado para evitar conflicto
from microservice_users.app.schemas.user import UserCreate, UserUpdate
from passlib.context import CryptContext # Para hashing de contraseñas
from fastapi import HTTPException, status

# Configurar el contexto de hashing para contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña plana contra una hasheada."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña."""
    return pwd_context.hash(password)

def get_user(db: Session, user_id: int) -> Optional[UserModel]:
    """Obtiene un usuario por su ID."""
    return db.query(UserModel).filter(UserModel.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[UserModel]:
    """Obtiene un usuario por su email."""
    return db.query(UserModel).filter(UserModel.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[UserModel]:
    """Obtiene una lista paginada de usuarios."""
    return db.query(UserModel).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> UserModel:
    """Crea un nuevo usuario en la base de datos."""
    # Verificar si el email ya existe
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Hashear la contraseña antes de guardarla
    hashed_password = get_password_hash(user.password)

    # Crear la instancia del modelo SQLAlchemy
    db_user = UserModel(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        is_active=True # Por defecto activo al crear
    )
    db.add(db_user) # Añadir a la sesión
    db.commit()     # Confirmar la transacción para guardar en BD
    db.refresh(db_user) # Refrescar el objeto con los datos de la BD (como el ID)
    return db_user

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[UserModel]:
    """Actualiza un usuario existente."""
    db_user = get_user(db, user_id)
    if not db_user:
        return None # O lanzar HTTPException(status_code=404, detail="User not found")

    update_data = user_update.model_dump(exclude_unset=True) # Obtener solo los campos enviados

    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data["password"])
        db_user.hashed_password = hashed_password
        del update_data["password"] # Eliminar para no intentar actualizarlo dos veces

    if "email" in update_data:
         # Verificar si el nuevo email ya está en uso por otro usuario
        existing_user = get_user_by_email(db, update_data["email"])
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered by another user")
        db_user.email = update_data["email"]
        del update_data["email"] # Ya procesado

    # Actualizar los demás campos
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> Optional[UserModel]:
    """Elimina un usuario."""
    db_user = get_user(db, user_id)
    if not db_user:
         return None # O lanzar HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return db_user # Devuelve el usuario eliminado (o podrías devolver True/None)