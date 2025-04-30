

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QLabel,
    QHBoxLayout, QTabWidget, QInputDialog, QAbstractItemView, QLineEdit,
    QFormLayout, QFrame, QTextEdit
)
# !!! CAMBIO: Importar Qt desde QtCore !!!
from PyQt5.QtCore import Qt # Necesario para Qt.UserRole

try:
    from api_client.client import ApiClient
except ImportError:
    sys.exit("Error Crítico: Falta el cliente API. Asegúrate de que api_client/client.py exista y sea importable.")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Microservices Dashboard - Simulación Roles")
        self.setGeometry(100, 100, 850, 650)

        self.api_client = ApiClient()
        self.current_user_id = None
        self.current_role = "viewer" # Rol inicial

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # --- Crear Pestañas ---
        self.users_tab = QWidget()
        self.tabs.addTab(self.users_tab, "Usuarios")
        self.setup_users_ui()

        self.content_tab = QWidget()
        self.tabs.addTab(self.content_tab, "Contenido")
        self.setup_content_ui()

        self.metrics_tab = QWidget()
        self.tabs.addTab(self.metrics_tab, "Métricas")
        self.setup_metrics_ui()

        self.apply_role_permissions() # Aplicar permisos iniciales

    # --- Configuración de Interfaces por Pestaña ---

    def setup_users_ui(self):
        # (Sin cambios)
        layout = QVBoxLayout(self.users_tab)
        action_layout = QHBoxLayout()
        self.login_button = QPushButton("Simular Login (ID 1 = Admin)")
        self.login_button.clicked.connect(self.simulate_login)
        self.create_user_button = QPushButton("Crear Usuario")
        self.create_user_button.setToolTip("Acción requiere rol Admin")
        self.create_user_button.clicked.connect(self.create_new_user_dialog)
        self.delete_user_button = QPushButton("Borrar Usuario Seleccionado")
        self.delete_user_button.setToolTip("Acción requiere rol Admin")
        self.delete_user_button.clicked.connect(self.delete_selected_user)
        action_layout.addWidget(self.login_button)
        action_layout.addStretch()
        action_layout.addWidget(self.create_user_button)
        action_layout.addWidget(self.delete_user_button)
        layout.addLayout(action_layout)
        self.load_users_button = QPushButton("Cargar/Refrescar Usuarios")
        self.load_users_button.clicked.connect(self.load_user_data)
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(3)
        self.users_table.setHorizontalHeaderLabels(["ID", "Email", "Nombre Completo"])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.users_table.setAlternatingRowColors(True)
        self.users_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.users_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.users_table.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.load_users_button)
        layout.addWidget(self.users_table)
        self.load_user_data()

    def setup_content_ui(self):
        """Configura la interfaz de la pestaña de Contenido."""
        main_layout = QVBoxLayout(self.content_tab)

        # --- Sección para Agregar Contenido ---
        add_group_layout = QVBoxLayout()
        add_group_label = QLabel("<b>Agregar Nuevo Contenido</b>")
        add_group_label.setAlignment(Qt.AlignCenter)
        add_group_layout.addWidget(add_group_label)
        form_layout = QFormLayout()
        self.content_title_input = QLineEdit()
        self.content_author_id_input = QLineEdit()
        self.content_body_input = QTextEdit()
        self.content_body_input.setPlaceholderText("Cuerpo del contenido...")
        self.content_body_input.setFixedHeight(80)
        self.content_tags_input = QLineEdit()
        self.content_tags_input.setPlaceholderText("tag1, tag2, tag3")
        form_layout.addRow("Título:", self.content_title_input)
        form_layout.addRow("ID Autor:", self.content_author_id_input)
        form_layout.addRow("Cuerpo:", self.content_body_input)
        form_layout.addRow("Tags (separados por coma):", self.content_tags_input)
        add_group_layout.addLayout(form_layout)
        self.content_add_button = QPushButton("Agregar Contenido")
        self.content_add_button.setToolTip("Acción requiere rol Admin")
        self.content_add_button.clicked.connect(self.add_content_item)
        add_group_layout.addWidget(self.content_add_button, alignment=Qt.AlignCenter)
        self.content_status_label = QLabel("")
        self.content_status_label.setAlignment(Qt.AlignCenter)
        add_group_layout.addWidget(self.content_status_label)
        main_layout.addLayout(add_group_layout)

        # --- Separador Visual ---
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)

        # --- Sección para Mostrar Contenido ---
        display_group_layout = QVBoxLayout()
        self.load_content_button = QPushButton("Cargar/Refrescar Contenido")
        self.load_content_button.clicked.connect(self.load_content_data)
        display_group_layout.addWidget(self.load_content_button)
        self.content_table = QTableWidget()
        self.content_table.setColumnCount(4)
        self.content_table.setHorizontalHeaderLabels(["ID", "Título", "ID Autor", "Tags"])
        self.content_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.content_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.content_table.setAlternatingRowColors(True)
        self.content_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # !!! CAMBIO: Conectar señal de doble clic !!!
        self.content_table.itemDoubleClicked.connect(self.show_content_details)
        display_group_layout.addWidget(self.content_table)

        main_layout.addLayout(display_group_layout)
        self.load_content_data()

    def setup_metrics_ui(self):
        # (Sin cambios)
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

    # --- Lógica de Carga de Datos ---
    def load_user_data(self):
        # (Sin cambios)
        print("Cargando datos de usuarios...")
        self.users_table.setRowCount(0)
        users_list = self.api_client.get_users(limit=200)
        if users_list is not None and users_list is not False:
            self.populate_users_table(users_list)
        else:
            print("No se pudieron cargar los datos de usuarios o no hay datos.")

    def load_content_data(self):
        # (Sin cambios)
        print("Cargando datos de contenido...")
        self.content_table.setRowCount(0)
        self.content_status_label.setText("Cargando contenido...")
        content_list = self.api_client.get_content_items(limit=200)
        if content_list is not None and content_list is not False:
            self.populate_content_table(content_list)
            self.content_status_label.setText("Contenido cargado.")
        else:
            print("No se pudieron cargar los datos de contenido o no hay datos.")
            self.content_status_label.setText("No se pudo cargar el contenido.")

    def load_metrics_data(self):
        # (Sin cambios)
        print("Cargando datos de métricas...")
        self.metrics_table.setRowCount(0)
        metrics_dict = self.api_client.get_all_metrics()
        if metrics_dict is not None and metrics_dict is not False:
            self.populate_metrics_table(metrics_dict)
        else:
            print("No se pudieron cargar los datos de métricas o no hay datos.")

    # --- Lógica para Poblar Tablas ---
    def populate_users_table(self, users: list):
        # (Sin cambios)
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
        """Puebla la tabla de contenido y almacena el body en los datos del ítem."""
        self.content_table.setRowCount(len(content_items))
        for row_index, item in enumerate(content_items):
            item_id_str = str(item.get("id") or item.get("_id", ""))
            item_title = item.get("title", "")
            item_body = item.get("body", "") # <<< OBTENER EL CUERPO
            item_author_id = str(item.get("author_id", "N/A"))
            tags_str = ", ".join(item.get("tags", []))

            # Crear los QTableWidgetItem
            id_item = QTableWidgetItem(item_id_str)
            title_item = QTableWidgetItem(item_title)
            author_id_item = QTableWidgetItem(item_author_id)
            tags_item = QTableWidgetItem(tags_str)

            # Alinear ID de autor
            author_id_item.setTextAlignment(Qt.AlignCenter)

            # !!! CAMBIO: Guardar el cuerpo como dato asociado al ítem del título !!!
            # Usamos Qt.UserRole como un espacio para datos personalizados.
            title_item.setData(Qt.UserRole, item_body)

            # Añadir ítems a la tabla
            self.content_table.setItem(row_index, 0, id_item)
            self.content_table.setItem(row_index, 1, title_item)
            self.content_table.setItem(row_index, 2, author_id_item)
            self.content_table.setItem(row_index, 3, tags_item)
        print(f"Tabla de contenido actualizada con {len(content_items)} filas.")

    def populate_metrics_table(self, metrics: dict):
        # (Sin cambios)
        sorted_metrics = sorted(metrics.items())
        self.metrics_table.setRowCount(len(sorted_metrics))
        for row_index, (name, value) in enumerate(sorted_metrics):
            name_item = QTableWidgetItem(name)
            value_item = QTableWidgetItem(str(value))
            value_item.setTextAlignment(Qt.AlignCenter)
            self.metrics_table.setItem(row_index, 0, name_item)
            self.metrics_table.setItem(row_index, 1, value_item)
        print(f"Tabla de métricas actualizada con {len(sorted_metrics)} filas.")

    # --- Método para Agregar Contenido ---
    def add_content_item(self):
        # (Sin cambios respecto a la versión corregida anterior)
        if self.current_role != "admin":
            QMessageBox.warning(self, "Permiso Denegado", "Solo administradores pueden agregar contenido.")
            return
        titulo = self.content_title_input.text().strip()
        body = self.content_body_input.toPlainText().strip()
        id_autor_str = self.content_author_id_input.text().strip()
        tags_str = self.content_tags_input.text().strip()
        if not titulo or not body or not id_autor_str:
            QMessageBox.warning(self, "Campos Requeridos", "Los campos 'Título', 'Cuerpo' y 'ID Autor' son obligatorios.")
            return
        tags_list = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        try:
            author_id_int = int(id_autor_str)
        except ValueError:
            QMessageBox.warning(self, "Entrada Inválida", "El 'ID Autor' debe ser un número entero.")
            return
        payload = {
            "title": titulo,
            "body": body,
            "author_id": author_id_int,
            "tags": tags_list
        }
        self.content_status_label.setText("Agregando contenido...")
        print(f"Intentando crear contenido con payload: {payload}")
        response_data = self.api_client.create_content_item(payload)
        if response_data is not None and response_data is not False:
            new_id = str(response_data.get("id") or response_data.get("_id", "N/A"))
            self.content_status_label.setText(f"Contenido agregado con ID: {new_id}")
            QMessageBox.information(self, "Éxito", f"Contenido '{titulo}' agregado correctamente.")
            self.content_title_input.clear()
            self.content_author_id_input.clear()
            self.content_tags_input.clear()
            self.content_body_input.clear()
            self.load_content_data()
        elif response_data is False:
             self.content_status_label.setText("Error al agregar contenido (ver consola o logs del cliente API).")
        else:
             self.content_status_label.setText("Respuesta inesperada del servidor.")
             QMessageBox.warning(self, "Respuesta Inesperada", "Se recibió una respuesta no esperada al agregar contenido.")


    # --- Lógica para Acciones de Admin (Usuarios) ---
    def create_new_user_dialog(self):
        # (Sin cambios)
        if self.current_role != "admin":
            QMessageBox.warning(self, "Permiso Denegado", "Solo administradores pueden crear usuarios.")
            return
        email, ok1 = QInputDialog.getText(self, "Crear Usuario", "Email:", QLineEdit.Normal, "")
        if not ok1 or not email: return
        password, ok2 = QInputDialog.getText(self, "Crear Usuario", "Password:", QLineEdit.Password, "")
        if not ok2 or not password: return
        full_name, ok3 = QInputDialog.getText(self, "Crear Usuario", "Nombre Completo:", QLineEdit.Normal, "")
        if not ok3: return
        print(f"Intentando crear usuario: {email}...")
        response = self.api_client.create_user(email, password, full_name)
        if response is not False and response is not None:
             QMessageBox.information(self, "Éxito", f"Usuario '{email}' creado con ID: {response.get('id')}.")
             self.load_user_data()

    def delete_selected_user(self):
        # (Sin cambios)
        if self.current_role != "admin":
            QMessageBox.warning(self, "Permiso Denegado", "Solo administradores pueden eliminar usuarios.")
            return
        selected_rows = self.users_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Error", "Selecciona un usuario para eliminar.")
            return
        selected_row = selected_rows[0].row()
        id_item = self.users_table.item(selected_row, 0)
        email_item = self.users_table.item(selected_row, 1)
        if not id_item:
            QMessageBox.critical(self, "Error", "No se pudo obtener el ID.")
            return
        try:
            user_id = int(id_item.text())
            user_email = email_item.text() if email_item else f"ID {user_id}"
            confirm = QMessageBox.question(self, "Confirmar", f"Eliminar usuario '{user_email}' (ID: {user_id})?",
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if confirm == QMessageBox.Yes:
                print(f"Intentando eliminar usuario ID: {user_id}...")
                response = self.api_client.delete_user(user_id)
                if response is None:
                     QMessageBox.information(self, "Éxito", f"Usuario '{user_email}' eliminado.")
                     self.load_user_data()
        except ValueError:
             QMessageBox.critical(self, "Error", f"ID '{id_item.text()}' inválido.")
        except Exception as e:
             QMessageBox.critical(self, "Error Inesperado", f"Ocurrió un error inesperado al eliminar: {e}")

    # --- Simulación de Login y Permisos ---
    def simulate_login(self):
        # (Sin cambios)
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
         """Aplica habilitación/deshabilitación de controles según el rol."""
         # (Sin cambios, ya incluía content_body_input)
         is_admin = (self.current_role == "admin")
         self.create_user_button.setEnabled(is_admin)
         self.delete_user_button.setEnabled(is_admin)
         self.content_add_button.setEnabled(is_admin)
         self.content_title_input.setEnabled(is_admin)
         self.content_author_id_input.setEnabled(is_admin)
         self.content_body_input.setEnabled(is_admin)
         self.content_tags_input.setEnabled(is_admin)
         self.increment_metric_button.setEnabled(is_admin)
         print(f"Permisos aplicados para rol: {self.current_role}")

    # --- Método para incrementar métrica ---
    def increment_metric(self, metric_name):
         # (Sin cambios)
         if self.current_role != "admin":
             QMessageBox.warning(self, "Permiso Denegado", "Solo administradores pueden modificar métricas.")
             return
         print(f"Intentando incrementar métrica: {metric_name}")
         response_data = self.api_client.increment_metric(metric_name)
         if response_data is not None and response_data is not False:
             print(f"Métrica '{metric_name}' incrementada.")
             self.load_metrics_data()

    # !!! NUEVO MÉTODO: Para mostrar detalles al hacer doble clic !!!
    def show_content_details(self, item: QTableWidgetItem):
        """Muestra el cuerpo del contenido en un QMessageBox al hacer doble clic."""
        # Asegurarse de que el evento viene de la columna correcta (Título, columna 1)
        # o que el item tenga los datos que esperamos
        if item and item.column() == 1: # Columna del Título
            body_text = item.data(Qt.UserRole) # Recuperar el cuerpo guardado
            if body_text:

                 msg_box = QMessageBox(self) # Pasar 'self' como padre
                 msg_box.setWindowTitle(f"Detalle: {item.text()}") # Usar título del ítem
                 msg_box.setText("Cuerpo del Contenido:")

                 msg_box.setInformativeText(body_text)
                 msg_box.setIcon(QMessageBox.Information)
                 msg_box.setStandardButtons(QMessageBox.Ok)
                 msg_box.exec_() # Mostrar el diálogo
            else:
                 # Si no hay texto guardado (inesperado si populate funciona bien)
                 QMessageBox.warning(self, "Sin Detalles", "No se encontró el cuerpo para este ítem.")
        # else: # Opcional: ignorar doble clic en otras columnas
        #    print(f"Doble clic en columna {item.column()}, ignorado.")


# --- Bloque Principal de Ejecución ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())