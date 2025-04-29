import requests
import json
import random

BASE_URL = "http://localhost:8000"  # URL del servicio de usuarios

def print_response(operation: str, response: requests.Response):
    """Imprime la respuesta de forma legible."""
    print(f"--- {operation} ---")
    print(f"Status Code: {response.status_code}")
    try:
        # Intenta imprimir el JSON si existe, si no, el texto
        print("Response JSON:", json.dumps(response.json(), indent=2))
    except json.JSONDecodeError:
        print("Response Text:", response.text)
    print("-" * (len(operation) + 8))
    print() # Línea en blanco para separar

def create_user(email: str, password: str, full_name: str = "Test User") -> requests.Response:
    """Llama a la API para crear un usuario."""
    url = f"{BASE_URL}/users/"
    payload = {"email": email, "password": password, "full_name": full_name}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload)
    print_response(f"Crear Usuario ({email})", response)
    return response

def get_all_users(skip: int = 0, limit: int = 10) -> requests.Response:
    """Llama a la API para obtener todos los usuarios."""
    url = f"{BASE_URL}/users/?skip={skip}&limit={limit}"
    response = requests.get(url)
    print_response(f"Obtener Todos los Usuarios (skip={skip}, limit={limit})", response)
    return response

def get_user_by_id(user_id: int) -> requests.Response:
    """Llama a la API para obtener un usuario específico."""
    url = f"{BASE_URL}/users/{user_id}"
    response = requests.get(url)
    print_response(f"Obtener Usuario ID={user_id}", response)
    return response

def update_user(user_id: int, update_data: dict) -> requests.Response:
    """Llama a la API para actualizar un usuario."""
    url = f"{BASE_URL}/users/{user_id}"
    headers = {"Content-Type": "application/json"}
    response = requests.put(url, headers=headers, json=update_data)
    print_response(f"Actualizar Usuario ID={user_id}", response)
    return response

def delete_user(user_id: int) -> requests.Response:
    """Llama a la API para eliminar un usuario."""
    url = f"{BASE_URL}/users/{user_id}"
    response = requests.delete(url)
    print_response(f"Eliminar Usuario ID={user_id}", response)
    return response

# --- Flujo de Prueba ---
if __name__ == "__main__":
    print(">>> Iniciando pruebas para Users API...")

    # 1. Crear un usuario
    random_suffix = random.randint(1000, 9999)
    user_email = f"testuser_{random_suffix}@example.com"
    create_resp = create_user(user_email, "securepassword123", f"Tester {random_suffix}")

    user_id_to_test = None
    if create_resp.status_code == 201:
        try:
            user_id_to_test = create_resp.json().get("id")
            print(f"Usuario creado con ID: {user_id_to_test}")
        except Exception as e:
            print(f"No se pudo obtener el ID del usuario creado: {e}")
    else:
        print("Fallo al crear usuario, deteniendo pruebas dependientes.")
        exit() # Salir si la creación falló

    # 2. Obtener todos los usuarios
    get_all_users(limit=5)

    # 3. Obtener el usuario específico que acabamos de crear
    if user_id_to_test:
        get_user_by_id(user_id_to_test)

        # 4. Actualizar el usuario creado
        update_payload = {"full_name": f"Tester {random_suffix} Updated", "is_active": False}
        update_user(user_id_to_test, update_payload)

        # Verificar la actualización
        get_user_by_id(user_id_to_test)

        # 5. Eliminar el usuario creado
        delete_user(user_id_to_test)

        # Verificar eliminación (debería dar 404)
        get_user_by_id(user_id_to_test)

    print(">>> Pruebas para Users API finalizadas.")