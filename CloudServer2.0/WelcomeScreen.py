from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QIcon, QPalette, QColor
from PyQt6.QtWidgets import QDialog, QLineEdit, QFormLayout, QPushButton, QMessageBox, QMainWindow

from Client import loginUser,registerUser
from Server import authenticateUser
from ProfileScreen import ProfileWindow


class Ui_MainWindow(object):
    def __init__(self, clientSocket):
        self.clientSocket = clientSocket

    def setupUi(self, MainWindow):
        self.main_window=MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 471)
        MainWindow.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.frame = QtWidgets.QFrame(parent=self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(210, 190, 391, 141))
        self.frame.setStyleSheet("background-color: rgb(67,92,92)")
        self.frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame.setObjectName("frame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName("verticalLayout")

        self.loginButton = QtWidgets.QPushButton(parent=self.frame)
        self.loginButton.setObjectName("loginButton")
        self.loginButton.clicked.connect(self.loginHandler)
        self.verticalLayout.addWidget(self.loginButton)

        self.signupButton = QtWidgets.QPushButton(parent=self.frame)
        self.signupButton.setObjectName("signupButton")
        self.signupButton.clicked.connect(self.signUpHandler)
        self.verticalLayout.addWidget(self.signupButton)

        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setStyleSheet("background-color: rgb(67,92,92)")
        self.label.setGeometry(QtCore.QRect(210, 160, 391, 50))
        self.label.setObjectName("label")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def loginHandler(self):
        dialog = QDialog()
        dialog.setWindowTitle("Login")
        form_layout = QFormLayout(dialog)

        usernameInput = QLineEdit()
        passwordInput = QLineEdit()
        passwordInput.setEchoMode(QLineEdit.EchoMode.Password)

        form_layout.addRow("Username:", usernameInput)
        form_layout.addRow("Password:", passwordInput)

        loginButton = QPushButton("Login")
        loginButton.clicked.connect(lambda: self.authenticate(usernameInput.text(), passwordInput.text(), dialog,self.main_window))
        form_layout.addRow(loginButton)

        dialog.exec()

    def authenticate(self, username, password, dialog,main_window):
        response, message = loginUser(self.clientSocket, username, password)
        if response:
            QMessageBox.information(dialog.parent(), "Login Successful", "You have logged in successfully.")
            dialog.accept()
            self.goToProfile(username, password,dialog,main_window)
        else:
            QMessageBox.warning(dialog.parent(), "Login Failed", message)



    def signUpHandler(self):
        dialog = QDialog()
        dialog.setWindowTitle("Sign Up")

        formLayout = QFormLayout(dialog)

        usernameInput = QLineEdit()
        passwordInput = QLineEdit()
        passwordInput.setEchoMode(QLineEdit.EchoMode.Password)

        formLayout.addRow("Username:", usernameInput)
        formLayout.addRow("Password:", passwordInput)

        signupButton = QPushButton("Sign Up")
        signupButton.clicked.connect(lambda: self.register(usernameInput.text(), passwordInput.text(), dialog))
        formLayout.addRow(signupButton)

        dialog.exec()


    def register(self,username,password,dialog):
        if self.clientSocket.fileno() == -1:
            QMessageBox.critical(dialog.parent(), "Connection Error", "Failed to connect to the server. Please try again later.")
            return

        try:
            response = registerUser(self.clientSocket, username, password)
            if response:
                QMessageBox.information(dialog.parent(), "Register Successful", "You have registered successfully.")
                dialog.accept()
            else:
                QMessageBox.warning(dialog.parent(), "Register Failed", "The username already exists or registration failed.")
        except BrokenPipeError:
            QMessageBox.critical(dialog.parent(), "Connection Error", "Failed to connect to the server. Please try again later.")



    def goToProfile(self,username,password,dialog,main_window):
        user=authenticateUser(username,password)
        if user:
            self.profileWindow=ProfileWindow(self.clientSocket,user)
            self.profileWindow.show()
            main_window.close()
        else:
            QMessageBox.warning(dialog.parent(),"Error","User not found")



    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        MainWindow.setWindowIcon(QIcon("icon.png"))
        MainWindow.setStyleSheet("background-color: rgb(90,114,114);")
        self.loginButton.setText(_translate("MainWindow", "Login"))
        self.signupButton.setText(_translate("MainWindow", "Sign Up"))
        self.label.setText(_translate("MainWindow",
                                      "<html><head/><body><p align=\"center\"><span style=\" font-size:20pt;\">MY CLOUD </span></p><p align=\"center\"><br/></p></body></html>"))


class MainWindow(QMainWindow):
    def __init__(self, clientSocket):
        super().__init__()
        self.ui = Ui_MainWindow(clientSocket)
        self.ui.setupUi(self)


