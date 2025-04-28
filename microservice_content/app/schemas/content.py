from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from beanie import Document, Link # Link es para relaciones (opcional aquí)
from pydantic import ConfigDict # Importar ConfigDict para model_config

# Ya no necesitamos PyObjectId helper, Beanie lo maneja

# --- Esquema Base (Usado para creación/actualización, NO es el Documento Beanie) ---
class ContentItemBase(BaseModel):
    title: str = Field(..., min_length=3, examples=["Mi Primer Artículo Async"])
    body: str = Field(..., examples=["Este es el cuerpo del artículo con Beanie..."])
    author_id: Optional[int] = Field(None, description="ID del usuario (del microservicio de usuarios)")
    tags: List[str] = Field([], examples=[["python", "beanie", "async"]])
    extra_data: Optional[Dict[str, Any]] = Field(None, description="Datos adicionales flexibles")
    # No incluimos created_at/updated_at aquí, Beanie puede manejarlos

class ContentItemCreate(ContentItemBase):
    """Esquema para recibir datos al crear."""
    pass

class ContentItemUpdate(BaseModel):
    """Esquema para recibir datos al actualizar (todos opcionales)."""
    # Usamos Optional[] para todos los campos que pueden actualizarse
    title: Optional[str] = Field(None, min_length=3, examples=["Título Actualizado Async"])
    body: Optional[str] = Field(None, examples=["Contenido actualizado con Beanie."])
    author_id: Optional[int] = None
    tags: Optional[List[str]] = None
    extra_data: Optional[Dict[str, Any]] = None

    # Permitir valores None explícitos si se envían en el JSON
    model_config = ConfigDict(validate_assignment=True)


# --- Modelo Beanie Document (Representa el documento en MongoDB) ---
class ContentItem(Document, ContentItemBase): # Hereda de Document y de Base
    """Modelo Beanie Document para ítems de contenido en MongoDB."""
    # id: PydanticObjectId lo añade Beanie automáticamente
    # Los campos de ContentItemBase se heredan

    # Beanie puede manejar timestamps automáticamente si se configura en Settings
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    # Configuración interna de Beanie
    class Settings:
        name = "content_items" # Nombre de la colección en MongoDB
        # Opcional: Añadir índices
        indexes = [
            "title", # Índice simple en el título
            [("tags", 1)], # Índice simple en el array de tags
            [("author_id", 1)], # Índice en author_id si buscas mucho por autor
        ]
        # Otras opciones:
        # use_state_management = True # Para rastrear cambios (útil con 'save()')
        # validate_on_save = True     # Validar con Pydantic antes de guardar

    # Configuración de Pydantic (opcional, para ejemplos en /docs)
    model_config = ConfigDict(
         json_schema_extra = {
            "example": {
                "id": "60d5ec49f7e4a6d8f8b4f3a1", # Beanie usa id, no _id por defecto en el modelo
                "title": "Artículo de Ejemplo con Beanie",
                "body": "Contenido del artículo...",
                "author_id": 1,
                "tags": ["beanie", "async"],
                "created_at": "2023-10-27T10:00:00Z",
                "updated_at": "2023-10-27T10:05:00Z",
                "extra_data": {"views": 150}
            }
        }
    )


# --- Esquema para la Respuesta API ---
# Usaremos el propio modelo Beanie (ContentItem) como respuesta general,
# ya que Pydantic V2 y Beanie manejan bien la serialización.
# Si necesitaras una estructura diferente, podrías definir un ContentItemResponse aquí.