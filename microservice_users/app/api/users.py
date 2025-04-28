from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from microservice_users.app.db.database import get_db
from microservice_users.app.schemas.user import User, UserCreate, UserUpdate
from microservice_users.app.services import user_service

# Crear un router para agrupar las rutas relacionadas con usuarios
router = APIRouter(
    prefix="/users", # Prefijo para todas las rutas en este router
    tags=["users"],   # Etiqueta para la documentación de Swagger UI
    responses={404: {"description": "Not found"}}, # Respuesta por defecto para 404
)

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED, summary="Create a new user")
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo usuario.

    - **email**: Correo electrónico único del usuario.
    - **password**: Contraseña del usuario (mínimo 8 caracteres).
    - **full_name**: Nombre completo (opcional).
    """
    # Podrías añadir validación extra aquí si es necesario antes de llamar al servicio
    db_user = user_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return user_service.create_user(db=db, user=user)


@router.get("/", response_model=List[User], summary="Get a list of users")
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Obtiene una lista paginada de usuarios.
    """
    users = user_service.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=User, summary="Get a specific user by ID")
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Obtiene un usuario específico por su ID.
    """
    db_user = user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=User, summary="Update a user")
def update_existing_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """
    Actualiza un usuario existente. Se pueden actualizar campos individuales.
    """
    db_user = user_service.update_user(db=db, user_id=user_id, user_update=user_update)
    if db_user is None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a user")
def delete_existing_user(user_id: int, db: Session = Depends(get_db)):
    """
    Elimina un usuario por su ID.
    Devuelve 204 No Content si tiene éxito.
    """
    deleted_user = user_service.delete_user(db=db, user_id=user_id)
    if deleted_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # No se devuelve contenido en un 204
    return None # O return Response(status_code=status.HTTP_204_NO_CONTENT)