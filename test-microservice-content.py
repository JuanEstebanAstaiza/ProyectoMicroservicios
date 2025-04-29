import requests
import json
import random

BASE_URL = "http://localhost:8001"  # URL del servicio de contenido

def print_response(operation: str, response: requests.Response):
    """Imprime la respuesta de forma legible."""
    print(f"--- {operation} ---")
    print(f"Status Code: {response.status_code}")
    try:
        print("Response JSON:", json.dumps(response.json(), indent=2))
    except json.JSONDecodeError:
        print("Response Text:", response.text)
    print("-" * (len(operation) + 8))
    print()

def create_content_item(title: str, body: str, author_id: int = None, tags: list = None) -> requests.Response:
    """Llama a la API para crear un ítem de contenido."""
    url = f"{BASE_URL}/content/"
    payload = {"title": title, "body": body}
    if author_id is not None:
        payload["author_id"] = author_id
    if tags is not None:
        payload["tags"] = tags
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload)
    print_response(f"Crear Ítem Contenido ({title})", response)
    return response

def get_all_content_items(skip: int = 0, limit: int = 10) -> requests.Response:
    """Llama a la API para obtener todos los ítems de contenido."""
    url = f"{BASE_URL}/content/?skip={skip}&limit={limit}"
    response = requests.get(url)
    print_response(f"Obtener Todos los Ítems (skip={skip}, limit={limit})", response)
    return response

def get_content_item_by_id(item_id: str) -> requests.Response:
    """Llama a la API para obtener un ítem específico."""
    url = f"{BASE_URL}/content/{item_id}"
    response = requests.get(url)
    print_response(f"Obtener Ítem ID={item_id}", response)
    return response

def update_content_item(item_id: str, update_data: dict) -> requests.Response:
    """Llama a la API para actualizar un ítem."""
    url = f"{BASE_URL}/content/{item_id}"
    headers = {"Content-Type": "application/json"}
    response = requests.put(url, headers=headers, json=update_data)
    print_response(f"Actualizar Ítem ID={item_id}", response)
    return response

def delete_content_item(item_id: str) -> requests.Response:
    """Llama a la API para eliminar un ítem."""
    url = f"{BASE_URL}/content/{item_id}"
    response = requests.delete(url)
    print_response(f"Eliminar Ítem ID={item_id}", response)
    return response

# --- Flujo de Prueba ---
if __name__ == "__main__":
    print(">>> Iniciando pruebas para Content API...")

    # Asumir que existe un usuario con ID 1 (creado desde el otro script o manualmente)
    test_author_id = 1

    # 1. Crear un ítem de contenido
    random_suffix = random.randint(1000, 9999)
    item_title = f"Artículo de Prueba {random_suffix}"
    item_body = "Este es el cuerpo del artículo generado por el script de prueba."
    create_resp = create_content_item(item_title, item_body, author_id=test_author_id, tags=["python", "test"])

    item_id_to_test = None
    if create_resp.status_code == 201:
        try:
            # El ID de MongoDB está en la respuesta JSON (puede llamarse 'id' o '_id' dependiendo de tu schema Beanie/Pydantic)
            # Adaptar si tu respuesta tiene el ID con otro nombre
            response_json = create_resp.json()
            if "id" in response_json:
                 item_id_to_test = response_json.get("id")
            elif "_id" in response_json: # Si el schema usa alias _id
                 item_id_to_test = response_json.get("_id")

            if item_id_to_test:
                print(f"Ítem creado con ID: {item_id_to_test}")
            else:
                print("No se encontró 'id' o '_id' en la respuesta JSON.")

        except Exception as e:
            print(f"No se pudo obtener el ID del ítem creado: {e}")
    else:
        print("Fallo al crear ítem, deteniendo pruebas dependientes.")
        exit() # Salir si la creación falló

    if not item_id_to_test:
        print("No se pudo obtener ID para continuar las pruebas.")
        exit()

    # 2. Obtener todos los ítems
    get_all_content_items(limit=5)

    # 3. Obtener el ítem específico que acabamos de crear
    get_content_item_by_id(item_id_to_test)

    # 4. Actualizar el ítem creado
    update_payload = {"body": "Contenido actualizado por el script.", "tags": ["python", "test", "updated"]}
    update_content_item(item_id_to_test, update_payload)

    # Verificar la actualización
    get_content_item_by_id(item_id_to_test)

    # 5. Eliminar el ítem creado
    delete_content_item(item_id_to_test)

    # Verificar eliminación (debería dar 404)
    get_content_item_by_id(item_id_to_test)

    print(">>> Pruebas para Content API finalizadas.")