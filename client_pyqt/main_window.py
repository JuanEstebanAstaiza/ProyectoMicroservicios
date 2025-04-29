# Archivo: client_pyqt/main_window.py

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QLabel,
    QHBoxLayout, QTabWidget, QInputDialog, QAbstractItemView, QLineEdit
)
from PyQt5.QtCore import Qt, QTimer
try:
    from api_client.client import ApiClient
except ImportError:
    sys.exit("Error Crítico: Falta el cliente API. Asegúrate de que api_client/__init__.py exista.")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Microservices Dashboard - Simulación Roles")
        self.setGeometry(100, 100, 850, 650)

        self.api_client = ApiClient()
        self.current_user_id = None
        self.current_role = "viewer"

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # --- Crear Pestañas ---
        self.users_tab = QWidget()
        self.tabs.addTab(self.users_tab, "Usuarios")
        self.setup_users_ui() # Llama a este método que ahora incluye los nuevos botones

        self.content_tab = QWidget()
        self.tabs.addTab(self.content_tab, "Contenido")
        self.setup_content_ui()

        self.metrics_tab = QWidget()
        self.tabs.addTab(self.metrics_tab, "Métricas")
        self.setup_metrics_ui()

        self.apply_role_permissions() # Aplicar permisos iniciales

    # --- Configuración de Interfaces por Pestaña ---

    def setup_users_ui(self):
        """Configura la interfaz de la pestaña de Usuarios."""
        layout = QVBoxLayout(self.users_tab)

        # Layout para Login y Acciones Admin
        action_layout = QHBoxLayout()
        self.login_button = QPushButton("Simular Login (ID 1 = Admin)")
        self.login_button.clicked.connect(self.simulate_login)

        # NUEVO: Botón Crear Usuario (Admin)
        self.create_user_button = QPushButton("Crear Usuario")
        self.create_user_button.setToolTip("Acción requiere rol Admin")
        self.create_user_button.clicked.connect(self.create_new_user_dialog)

        # NUEVO: Botón Borrar Usuario (Admin)
        self.delete_user_button = QPushButton("Borrar Usuario Seleccionado")
        self.delete_user_button.setToolTip("Acción requiere rol Admin")
        self.delete_user_button.clicked.connect(self.delete_selected_user)

        action_layout.addWidget(self.login_button)
        action_layout.addStretch() # Espacio
        action_layout.addWidget(self.create_user_button)
        action_layout.addWidget(self.delete_user_button)
        layout.addLayout(action_layout) # Añadir layout de acciones

        # Botón y Tabla (como antes)
        self.load_users_button = QPushButton("Cargar/Refrescar Usuarios")
        self.load_users_button.clicked.connect(self.load_user_data)

        self.users_table = QTableWidget()
        self.users_table.setColumnCount(3)
        self.users_table.setHorizontalHeaderLabels(["ID", "Email", "Nombre Completo"])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.users_table.setAlternatingRowColors(True)
        self.users_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.users_table.setSelectionBehavior(QAbstractItemView.SelectRows) # Seleccionar filas enteras
        self.users_table.setSelectionMode(QAbstractItemView.SingleSelection) # Solo una fila a la vez

        layout.addWidget(self.load_users_button)
        layout.addWidget(self.users_table)
        self.load_user_data() # Carga inicial

    def setup_content_ui(self):
        # (Sin cambios respecto a la versión anterior)
        layout = QVBoxLayout(self.content_tab)
        self.load_content_button = QPushButton("Cargar/Refrescar Contenido")
        self.load_content_button.clicked.connect(self.load_content_data)
        self.content_table = QTableWidget()
        self.content_table.setColumnCount(4)
        self.content_table.setHorizontalHeaderLabels(["ID", "Título", "ID Autor", "Tags"])
        self.content_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.content_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.content_table.setAlternatingRowColors(True)
        self.content_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.load_content_button)
        layout.addWidget(self.content_table)
        self.load_content_data()

    def setup_metrics_ui(self):
        # (Sin cambios respecto a la versión anterior)
        layout = QVBoxLayout(self.metrics_tab)
        self.load_metrics_button = QPushButton("Cargar/Refrescar Métricas")
        self.load_metrics_button.clicked.connect(self.load_metrics_data)
        self.increment_button_layout = QHBoxLayout()
        self.increment_metric_button = QPushButton("Incrementar 'homepage_visits'")
        self.increment_metric_button.setToolTip("Acción requiere rol Admin")
        self.increment_metric_button.clicked.connect(lambda: self.increment_metric("homepage_visits"))
        self.increment_button_layout.addWidget(self.increment_metric_button)
        self.increment_button_layout.addStretch()
        self.metrics_table = QTableWidget()
        self.metrics_table.setColumnCount(2)
        self.metrics_table.setHorizontalHeaderLabels(["Métrica", "Valor"])
        self.metrics_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.metrics_table.setAlternatingRowColors(True)
        self.metrics_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.load_metrics_button)
        layout.addLayout(self.increment_button_layout)
        layout.addWidget(self.metrics_table)
        self.load_metrics_data()

    # --- Lógica de Carga de Datos (sin cambios) ---
    def load_user_data(self):
        print("Cargando datos de usuarios...")
        users_list = self.api_client.get_users(limit=200)
        if users_list is not None and users_list is not False: # Verificar que no sea error (False)
            self.populate_users_table(users_list)
        else:
            self.users_table.setRowCount(0)

    def load_content_data(self):
        print("Cargando datos de contenido...")
        content_list = self.api_client.get_content_items(limit=200)
        if content_list is not None and content_list is not False:
            self.populate_content_table(content_list)
        else:
            self.content_table.setRowCount(0)

    def load_metrics_data(self):
        print("Cargando datos de métricas...")
        metrics_dict = self.api_client.get_all_metrics()
        if metrics_dict is not None and metrics_dict is not False:
            self.populate_metrics_table(metrics_dict)
        else:
            self.metrics_table.setRowCount(0)

    # --- Lógica para Poblar Tablas (sin cambios) ---
    def populate_users_table(self, users: list):
        # (Igual que antes)
        self.users_table.setRowCount(len(users))
        for row_index, user in enumerate(users):
            user_id_item = QTableWidgetItem(str(user.get("id", "")))
            email_item = QTableWidgetItem(user.get("email", ""))
            full_name_item = QTableWidgetItem(user.get("full_name", "N/A"))
            user_id_item.setTextAlignment(Qt.AlignCenter)
            self.users_table.setItem(row_index, 0, user_id_item)
            self.users_table.setItem(row_index, 1, email_item)
            self.users_table.setItem(row_index, 2, full_name_item)
        print(f"Tabla de usuarios actualizada con {len(users)} filas.")

    def populate_content_table(self, content_items: list):
        # (Igual que antes)
        self.content_table.setRowCount(len(content_items))
        for row_index, item in enumerate(content_items):
            item_id_str = item.get("id") or item.get("_id", "")
            item_id_item = QTableWidgetItem(str(item_id_str))
            title_item = QTableWidgetItem(item.get("title", ""))
            author_id_item = QTableWidgetItem(str(item.get("author_id", "N/A")))
            tags_item = QTableWidgetItem(", ".join(item.get("tags", [])))
            author_id_item.setTextAlignment(Qt.AlignCenter)
            self.content_table.setItem(row_index, 0, item_id_item)
            self.content_table.setItem(row_index, 1, title_item)
            self.content_table.setItem(row_index, 2, author_id_item)
            self.content_table.setItem(row_index, 3, tags_item)
        print(f"Tabla de contenido actualizada con {len(content_items)} filas.")

    def populate_metrics_table(self, metrics: dict):
        # (Igual que antes)
        sorted_metrics = sorted(metrics.items())
        self.metrics_table.setRowCount(len(sorted_metrics))
        for row_index, (name, value) in enumerate(sorted_metrics):
            name_item = QTableWidgetItem(name)
            value_item = QTableWidgetItem(str(value))
            value_item.setTextAlignment(Qt.AlignCenter)
            self.metrics_table.setItem(row_index, 0, name_item)
            self.metrics_table.setItem(row_index, 1, value_item)
        print(f"Tabla de métricas actualizada con {len(sorted_metrics)} filas.")

    # --- NUEVO: Lógica para Acciones de Admin ---

    def create_new_user_dialog(self):
        """Abre diálogos para obtener datos y crear un nuevo usuario."""
        if self.current_role != "admin":
            QMessageBox.warning(self, "Permiso Denegado", "Solo administradores pueden crear usuarios.")
            return

        email, ok1 = QInputDialog.getText(self, "Crear Usuario", "Email:", QLineEdit.Normal, "")
        if not ok1 or not email:
            return # Cancelado o vacío

        # Usar NoEcho para la contraseña
        password, ok2 = QInputDialog.getText(self, "Crear Usuario", "Password:", QLineEdit.Password, "")
        if not ok2 or not password:
            return # Cancelado o vacío

        full_name, ok3 = QInputDialog.getText(self, "Crear Usuario", "Nombre Completo:", QLineEdit.Normal, "")
        if not ok3: # Nombre completo puede ser vacío, pero no cancelar
             return # Cancelado

        print(f"Intentando crear usuario: {email}...")
        response = self.api_client.create_user(email, password, full_name)

        # El ApiClient ya muestra errores, aquí solo confirmamos éxito y refrescamos
        if response is not False and response is not None: # Si no fue error y devolvió datos
             QMessageBox.information(self, "Éxito", f"Usuario '{email}' creado correctamente con ID: {response.get('id')}.")
             self.load_user_data() # Refrescar tabla
        # Si response es False, ApiClient ya mostró el error
        # Si response es None (inesperado para POST exitoso), podría indicar un problema

    def delete_selected_user(self):
        """Elimina el usuario seleccionado en la tabla."""
        if self.current_role != "admin":
            QMessageBox.warning(self, "Permiso Denegado", "Solo administradores pueden eliminar usuarios.")
            return

        selected_rows = self.users_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Error", "Por favor, selecciona un usuario de la tabla para eliminar.")
            return

        selected_row = selected_rows[0].row()
        id_item = self.users_table.item(selected_row, 0) # Columna ID
        email_item = self.users_table.item(selected_row, 1) # Columna Email (para mensaje)

        if not id_item:
            QMessageBox.critical(self, "Error", "No se pudo obtener el ID del usuario seleccionado.")
            return

        try:
            user_id = int(id_item.text())
            user_email = email_item.text() if email_item else f"ID {user_id}"

            # Confirmación
            confirm = QMessageBox.question(self, "Confirmar Eliminación",
                                           f"¿Estás seguro de que quieres eliminar al usuario '{user_email}' (ID: {user_id})?",
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if confirm == QMessageBox.Yes:
                print(f"Intentando eliminar usuario ID: {user_id}...")
                response = self.api_client.delete_user(user_id)

                # Verificar respuesta (delete_user devuelve None en éxito 204, False en error)
                if response is None:
                     QMessageBox.information(self, "Éxito", f"Usuario '{user_email}' eliminado correctamente.")
                     self.load_user_data() # Refrescar tabla
                elif response is False:
                     # ApiClient ya debería haber mostrado el error HTTP
                     pass
                else:
                     # Caso inesperado
                     QMessageBox.warning(self, "Respuesta Inesperada", f"Se recibió una respuesta inesperada al intentar eliminar: {response}")

        except ValueError:
             QMessageBox.critical(self, "Error", f"El ID '{id_item.text()}' no es un número válido.")
        except Exception as e:
             QMessageBox.critical(self, "Error Inesperado", f"Ocurrió un error al intentar eliminar: {e}")


    # --- Simulación de Login y Permisos (Modificada) ---

    def simulate_login(self):
        user_id, ok = QInputDialog.getInt(self, "Simular Login", "Introduce ID de Usuario (ID=1 es Admin):", 1, 1, 1000, 1)
        if ok:
            self.current_user_id = user_id
            if self.current_user_id == 1:
                self.current_role = "admin"
                self.setWindowTitle("Microservices Dashboard - ROL: ADMIN")
            else:
                self.current_role = "viewer"
                self.setWindowTitle(f"Microservices Dashboard - ROL: Viewer (ID: {self.current_user_id})")
            print(f"Usuario simulado: ID={self.current_user_id}, Rol={self.current_role}")
            self.apply_role_permissions()
        else:
             print("Login simulado cancelado.")

    def apply_role_permissions(self):
         is_admin = (self.current_role == "admin")
         # Habilitar/deshabilitar botones de admin
         self.increment_metric_button.setEnabled(is_admin)
         self.create_user_button.setEnabled(is_admin)
         self.delete_user_button.setEnabled(is_admin)
         # Añadir más aquí si es necesario...
         print(f"Permisos aplicados para rol: {self.current_role}")