from beanie import PydanticObjectId # Tipo específico de Beanie para IDs
from beanie.exceptions import DocumentNotFound
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime

# Importar el modelo Beanie y los esquemas de entrada
from microservice_content.app.schemas.content import ContentItem, ContentItemCreate, ContentItemUpdate

async def create_content_item_service(item_data: ContentItemCreate) -> ContentItem:
    """Crea un nuevo ítem de contenido usando Beanie."""
    # Crear una instancia del modelo Beanie Document
    item = ContentItem(**item_data.model_dump())
    # Beanie se encarga de created_at/updated_at si se configuran bien
    item.created_at = datetime.utcnow()
    item.updated_at = datetime.utcnow()
    try:
        await item.insert() # Método insert de Beanie
        return item
    except Exception as e:
        # Manejar posibles errores de duplicidad de índices únicos si los tuvieras
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error al crear el ítem: {e}")

async def get_content_item_service(item_id: PydanticObjectId) -> Optional[ContentItem]:
    """Obtiene un ítem de contenido por su ID usando Beanie."""
    try:
        # Usar el método get de Beanie (equivalente a find_one por ID)
        item = await ContentItem.get(item_id)
        return item
    except DocumentNotFound: # Beanie lanza esta excepción específica
         return None
    except Exception as e:
         # Otros posibles errores
         print(f"Error inesperado al buscar item {item_id}: {e}")
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno al buscar el ítem.")


async def get_all_content_items_service(skip: int = 0, limit: int = 10) -> List[ContentItem]:
    """Obtiene una lista paginada de ítems usando Beanie."""
    try:
        # Usar find con skip/limit
        items = await ContentItem.find(skip=skip, limit=limit).to_list()
        return items
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error al obtener la lista de ítems: {e}")

async def update_content_item_service(item_id: PydanticObjectId, item_update: ContentItemUpdate) -> Optional[ContentItem]:
    """Actualiza un ítem de contenido usando Beanie."""
    item = await get_content_item_service(item_id) # Primero, buscar el item
    if not item:
        return None

    # Obtener los datos de actualización, excluyendo los no establecidos (None por defecto)
    update_data = item_update.model_dump(exclude_unset=True)

    if not update_data:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No hay datos válidos para actualizar.")

    # Actualizar la fecha
    update_data["updated_at"] = datetime.utcnow()

    try:
        # Usar el método update de Beanie con el operador $set
        await item.update({"$set": update_data})
        # Después de actualizar, volver a obtener el item para devolver el estado más reciente
        updated_item = await ContentItem.get(item_id)
        return updated_item
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error al actualizar el ítem {item_id}: {e}")


async def delete_content_item_service(item_id: PydanticObjectId) -> bool:
    """Elimina un ítem de contenido usando Beanie."""
    item = await get_content_item_service(item_id)
    if not item:
        return False # No encontrado

    try:
        await item.delete() # Método delete de Beanie
        return True
    except Exception as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error al eliminar el ítem {item_id}: {e}")