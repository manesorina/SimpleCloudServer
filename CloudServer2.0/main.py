import sys
import socket
import ssl
from PyQt6.QtWidgets import QApplication, QMainWindow
from WelcomeScreen import Ui_MainWindow



def create_client_socket():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("0.0.0.0", 5000))
    return client_socket

if __name__ == "__main__":
    app = QApplication(sys.argv)

    client_socket = create_client_socket()

    main_window = QMainWindow()
    ui = Ui_MainWindow(client_socket)
    ui.setupUi(main_window)

    main_window.show()

    sys.exit(app.exec())