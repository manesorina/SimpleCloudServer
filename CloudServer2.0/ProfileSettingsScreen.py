from __future__ import annotations
from PyQt6 import QtCore, QtGui, QtWidgets
from typing import TYPE_CHECKING

from Client import deleteAccount,changePassword,changeUsername
from PyQt6.QtWidgets import QMainWindow, QMessageBox
import WelcomeScreen


if TYPE_CHECKING:
    from ProfileScreen import ProfileWindow

class ProfileSettingsWindow(QMainWindow,):

    def __init__(self,clientSocket,user,parent: 'ProfileWindow' = None):
        super().__init__()
        self.clientSocket=clientSocket
        if isinstance(user, dict):
            self.user = user
            self.username = user.get('username', '')
            self.password = user.get('password', '')
        elif isinstance(user, bool):
            self.user = {'authenticated': user}
            self.username = ''
            self.password = ''
        else:
            self.user = {'unknown': True}
            self.username = ''
            self.password = ''
        self.parent: ProfileWindow = parent
        self.setupUi(self)
        self.updateUserInfo()




    def setupUi(self, MainWindow):

        MainWindow.setObjectName("ProfileSettings")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.currentUsernameLabel = QtWidgets.QLabel(parent=self.centralwidget)
        self.currentUsernameLabel.setGeometry(QtCore.QRect(40, 120, 151, 24))
        self.currentUsernameLabel.setObjectName("currentUsernameLabel")


        self.currentPasswordLabel = QtWidgets.QLabel(parent=self.centralwidget)
        self.currentPasswordLabel.setGeometry(QtCore.QRect(40, 200, 141, 24))
        self.currentPasswordLabel.setObjectName("currentPasswordLabel")

        self.usernameButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.usernameButton.setGeometry(QtCore.QRect(650, 100, 102, 32))
        self.usernameButton.setObjectName("usernameButton")
        self.usernameButton.setStyleSheet("background-color: rgb(46,80,80)")

        self.passwordButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.passwordButton.setGeometry(QtCore.QRect(650, 180, 102, 32))
        self.passwordButton.setObjectName("Password")
        self.passwordButton.setStyleSheet("background-color: rgb(46,80,80)")






        self.checkBox = QtWidgets.QCheckBox(parent=self.centralwidget)
        self.checkBox.setGeometry(QtCore.QRect(340, 200, 16, 21))
        self.checkBox.setText("Show Password")


        self.checkBox.setObjectName("checkBox")
        self.deleteButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.deleteButton.setGeometry(QtCore.QRect(340, 470, 102, 32))
        self.deleteButton.setObjectName("deleteButton")
        self.goBackToProfile = QtWidgets.QPushButton(parent=self.centralwidget)
        self.goBackToProfile.setGeometry(QtCore.QRect(690, 10, 102, 32))
        self.goBackToProfile.setObjectName("goBackToProfile")
        self.welcomeLabel = QtWidgets.QLabel(parent=self.centralwidget)
        self.welcomeLabel.setGeometry(QtCore.QRect(10, 10, 191, 24))
        self.welcomeLabel.setObjectName("welcomeLabel")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.usernameButton.clicked.connect(self.changeUsername)
        self.passwordButton.clicked.connect(self.changePassword)
        self.deleteButton.clicked.connect(self.deleteAccount)
        self.goBackToProfile.clicked.connect(self.goBack)
        self.checkBox.toggled.connect(self.togglePasswordVisibility)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def updateUserInfo(self):
        if self.username:
            self.welcomeLabel.setText(f"Hello, {self.username}")
            self.currentUsernameLabel.setText(f"Username: {self.username}")
        else:
            self.welcomeLabel.setText("Hello, User")
            self.currentUsernameLabel.setText("Username: Unknown")

        self.currentPasswordLabel.setText("Password: **********")


    def changeUsername(self):
        newUsername, ok = QtWidgets.QInputDialog.getText(self, "Change Username", "Enter new username:")
        if ok and newUsername:
            if changeUsername(self.clientSocket, newUsername):
                QMessageBox.information(self, "Success", "Username changed successfully!")
                self.username = newUsername
                if isinstance(self.user, dict):
                    self.user['username'] = newUsername
                self.welcomeLabel.setText(f"Hello, {newUsername}")
                self.currentUsernameLabel.setText(f"Username: {newUsername}")
            else:
                QMessageBox.warning(self, "Error", "Username already exists.")


    def changePassword(self):
        newPassword, ok = QtWidgets.QInputDialog.getText(
            self, "Change Password", "Enter new password:",
            QtWidgets.QLineEdit.EchoMode.Password
        )
        if ok and newPassword:
            if changePassword(self.clientSocket, newPassword):
                QMessageBox.information(self, "Success", "Password changed successfully!")
                self.password = newPassword
                if isinstance(self.user, dict):
                    self.user['password'] = newPassword

                if self.checkBox.isChecked():
                    self.currentPasswordLabel.setText(f"Password: {newPassword}")
                else:
                    self.currentPasswordLabel.setText("Password: **********")
            else:
                QMessageBox.warning(self, "Error", "Password change failed.")


    def deleteAccount(self):
        reply = QMessageBox.question(self, "Delete Account",
                                     "Are you sure you want to delete your account? This action is irreversible.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if deleteAccount(self.clientSocket):
                QMessageBox.information(self, "Account Deleted", "Your account has been deleted.")

                self.close()
                if self.parent:
                    self.parent.close()


                self.welcome_screen = WelcomeScreen(self.clientSocket)
                self.welcome_screen.show()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete account.")


    def goBack(self):
        self.close()
        self.parent.show()



    def togglePasswordVisibility(self):
        if self.checkBox.isChecked():
            if self.password:
                self.currentPasswordLabel.setText(f"Password: {self.password}")
            else:
                self.currentPasswordLabel.setText("Password: Not available")
        else:
            self.currentPasswordLabel.setText("Password: **********")



    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("ProfileSettings", "MainWindow"))
        MainWindow.setStyleSheet("background-color: rgb(90,114,114)")
        self.currentUsernameLabel.setText(_translate("ProfileSettings", "Username: "))
        self.currentPasswordLabel.setText(_translate("ProfileSettings", "Password:"))
        self.usernameButton.setText(_translate("ProfileSettings", "Change"))
        self.passwordButton.setText(_translate("ProfileSettings", "Change"))
        self.deleteButton.setText(_translate("ProfileSettings", "Delete Account"))
        self.goBackToProfile.setText(_translate("ProfileSettings", "Back to Profile"))
        self.welcomeLabel.setText(_translate("ProfileSettings", "Hello, insert username"))



