
import requests
from PyQt5.QtWidgets import QMessageBox

# URLs base de las APIs
USERS_API_URL = "http://localhost:8000"
CONTENT_API_URL = "http://localhost:8020"
METRICS_API_URL = "http://localhost:8002"

class ApiClient:
    """Clase para manejar las llamadas a las APIs de los microservicios."""

    def _make_request(self, method: str, url: str, **kwargs):
        """Método base para realizar peticiones y manejar errores comunes."""
        try:
            # Asegurar que los datos JSON se pasen correctamente si existen
            if 'json' in kwargs:
                kwargs['headers'] = kwargs.get('headers', {})
                kwargs['headers']['Content-Type'] = 'application/json'

            response = requests.request(method, url, timeout=10, **kwargs) # Aumentar timeout
            response.raise_for_status()
            # Devolver JSON si la respuesta no está vacía y el status no es 204 (No Content)
            if response.status_code != 204 and response.content:
                 return response.json()
            else:
                 return None # Devolver None para éxito sin contenido (ej. DELETE) o vacío
        except requests.exceptions.ConnectionError:
            print(f"Error de Conexión: No se pudo conectar a {url}.")
            QMessageBox.warning(None, "Error de Conexión", f"No se pudo conectar a {url}. ¿Están los servicios corriendo?")
        except requests.exceptions.Timeout:
            print(f"Timeout: La petición a {url} tardó demasiado.")
            QMessageBox.warning(None, "Timeout", f"La petición a {url} tardó demasiado.")
        except requests.exceptions.HTTPError as e:
            error_detail = f"Error en la petición a {url}: {e.response.status_code}"
            try:
                error_data = e.response.json()
                error_detail += f"\n{error_data.get('detail', e.response.text)}"
            except:
                 error_detail += f"\n{e.response.text}"
            print(error_detail)
            QMessageBox.warning(None, "Error HTTP", error_detail)
        except requests.exceptions.RequestException as e:
            print(f"Error Inesperado (requests): {e}")
            QMessageBox.critical(None, "Error", f"Ocurrió un error inesperado al contactar {url}: {e}")
        except Exception as e:
            print(f"Error General: {e}")
            QMessageBox.critical(None, "Error General", f"Ocurrió un error inesperado: {e}")

        # Devolver False explícitamente en caso de error para distinguirlo de éxito sin contenido (None)
        return False


    # --- Métodos para Users API ---
    def get_users(self, skip: int = 0, limit: int = 100) -> list | None | bool:
        url = f"{USERS_API_URL}/users/?skip={skip}&limit={limit}"
        return self._make_request("GET", url)

    def get_user(self, user_id: int) -> dict | None | bool:
        url = f"{USERS_API_URL}/users/{user_id}"
        return self._make_request("GET", url)

    # --- NUEVO: Método para Crear Usuario ---
    def create_user(self, email: str, password: str, full_name: str) -> dict | None | bool:
        """Crea un nuevo usuario."""
        url = f"{USERS_API_URL}/users/"
        payload = {"email": email, "password": password, "full_name": full_name}
        return self._make_request("POST", url, json=payload)

    # --- NUEVO: Método para Borrar Usuario ---
    def delete_user(self, user_id: int) -> None | bool:
        """Elimina un usuario por ID."""
        url = f"{USERS_API_URL}/users/{user_id}"
        # DELETE exitoso devuelve None (código 204), un error devuelve False
        return self._make_request("DELETE", url)

    # --- Métodos para Content API ---
    def get_content_items(self, skip: int = 0, limit: int = 10) -> list | None | bool:
        url = f"{CONTENT_API_URL}/content/?skip={skip}&limit={limit}"
        return self._make_request("GET", url)

    def get_content_item(self, item_id: str) -> dict | None | bool:
        url = f"{CONTENT_API_URL}/content/{item_id}"
        return self._make_request("GET", url)

    def create_content_item(self, payload: dict) -> dict | None | bool:
        """Crea un nuevo ítem de contenido."""
        url = f"{CONTENT_API_URL}/content/"  # Endpoint POST para crear
        # El método _make_request ya añade Content-Type: application/json
        # y maneja errores comunes.
        # Devuelve el JSON de la respuesta si éxito (201), None si 204 (no aplica aquí), False en error.
        return self._make_request("POST", url, json=payload)

    # --- Métodos para Metrics API ---
    def get_all_metrics(self) -> dict | None | bool:
         url = f"{METRICS_API_URL}/metrics/all"
         response_data = self._make_request("GET", url)
         # Manejar caso de error (False)
         if response_data is False:
             return False
         return response_data.get("metrics") if response_data else {} # Devolver dict vacío si no hay métricas

    def increment_metric(self, metric_name: str) -> dict | None | bool:
         url = f"{METRICS_API_URL}/metrics/increment/{metric_name}"
         return self._make_request("POST", url)