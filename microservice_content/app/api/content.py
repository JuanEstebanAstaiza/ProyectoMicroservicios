from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List
from beanie import PydanticObjectId # Importar el tipo de ID de Beanie

# Importar el modelo Beanie y los esquemas de entrada/actualización
from microservice_content.app.schemas.content import ContentItem, ContentItemCreate, ContentItemUpdate
# Importar las funciones del servicio (que ahora son async)
from microservice_content.app.services import content_service

router = APIRouter(
    prefix="/content",
    tags=["content"],
    responses={404: {"description": "Not found"}},
)

# --- Endpoints Async ---

@router.post("/", response_model=ContentItem, status_code=status.HTTP_201_CREATED, summary="Create content (async)")
async def create_item(item_data: ContentItemCreate = Body(...)):
    """Crea un ítem de contenido (versión async con Beanie)."""
    try:
        created_item = await content_service.create_content_item_service(item_data)
        return created_item
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=List[ContentItem], summary="Get content list (async)")
async def get_items(skip: int = 0, limit: int = 10):
    """Obtiene lista de ítems de contenido (versión async con Beanie)."""
    items = await content_service.get_all_content_items_service(skip=skip, limit=limit)
    return items


@router.get("/{item_id}", response_model=ContentItem, summary="Get content by ID (async)")
async def get_item(item_id: PydanticObjectId): # Usar PydanticObjectId para validación automática
    """Obtiene un ítem por ID (versión async con Beanie)."""
    item = await content_service.get_content_item_service(item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content item not found")
    return item


@router.put("/{item_id}", response_model=ContentItem, summary="Update content (async)")
async def update_item(item_id: PydanticObjectId, item_update: ContentItemUpdate = Body(...)):
    """Actualiza un ítem por ID (versión async con Beanie)."""
    updated_item = await content_service.update_content_item_service(item_id, item_update)
    if updated_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content item not found")
    return updated_item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete content (async)")
async def delete_item(item_id: PydanticObjectId):
    """Elimina un ítem por ID (versión async con Beanie)."""
    deleted = await content_service.delete_content_item_service(item_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content item not found")
    return None # Respuesta 204 sin contenido