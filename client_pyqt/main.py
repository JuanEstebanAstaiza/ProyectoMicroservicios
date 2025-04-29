# Archivo: client_pyqt/main.py

import sys
from PyQt5.QtWidgets import QApplication
# Importar la clase de la ventana principal desde main_window.py
from main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Crear e mostrar la ventana principal
    window = MainWindow()
    window.show()
    # Iniciar el bucle de eventos de la aplicación
    sys.exit(app.exec_())