import os.path

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QAction

from FileWidget import FileWidget
from ProfileSettingsScreen import ProfileSettingsWindow
from Client import uploadFile,listFiles
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QMenu





class ProfileWindow(QMainWindow):
    def __init__(self,clientSocket,user):
        super().__init__()
        self.clientSocket=clientSocket
        if isinstance(user, bool):
            self.authenticated = user
            self.username = ""
            self.password = ""
            self.user = {'authenticated': user}
        elif isinstance(user, dict):
            self.authenticated = True
            self.username = user.get('username', '')
            self.password = user.get('password', '')
            self.user = user
        else:
            self.authenticated = False
            self.username = ""
            self.password = ""
            self.user = {'authenticated': False}
        self.setupUi(self)
        self.file_count=0
        self.fileWidgets=[]







    def setupUi(self, MainWindow):
        self.mainWindow=MainWindow
        MainWindow.setObjectName("ProfileWindow")
        MainWindow.resize(800, 600)
        MainWindow.setWindowTitle("Profile")
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.logOutButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.logOutButton.setStyleSheet("background-color: rgb(46,80,80)")
        self.logOutButton.setGeometry(QtCore.QRect(660, 10, 121, 31))
        self.logOutButton.setObjectName("logOutButton")
        self.logOutButton.clicked.connect(self.logOut)

        self.accountSettingsButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.accountSettingsButton.setGeometry(QtCore.QRect(650, 50, 141, 32))
        self.accountSettingsButton.setStyleSheet("background-color: rgb(46,80,80)")
        self.accountSettingsButton.setObjectName("accountSettingsButton")
        self.accountSettingsButton.clicked.connect(self.openProfileSettings)

        self.scrollArea = QtWidgets.QScrollArea(parent=self.centralwidget)
        self.scrollArea.setGeometry(QtCore.QRect(20, 220, 761, 341))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")

        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")


        self.uploadButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.uploadButton.setStyleSheet("background-color: rgb(46,80,80)")
        self.uploadButton.setGeometry(QtCore.QRect(340, 140, 131, 32))
        self.uploadButton.setObjectName("uploadButton")
        self.uploadButton.clicked.connect(self.uploadFile)

        self.helloLabel = QtWidgets.QLabel(parent=self.centralwidget)
        self.uploadButton.setStyleSheet("background-color: rgb(46,80,80)")
        self.helloLabel.setGeometry(QtCore.QRect(20, 40, 141, 21))
        self.helloLabel.setText("insert username here")

        self.helloLabel_2 = QtWidgets.QLabel(parent=self.centralwidget)
        self.helloLabel_2.setGeometry(QtCore.QRect(20, 20, 121, 24))
        self.helloLabel_2.setText("Welcome,")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)




    def logOut(self):
        self.close()

    def uploadFile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Select File to Upload")
        if not filePath:
            return

        try:
            success = uploadFile(self.clientSocket, filePath)
            filename = os.path.basename(filePath)
            self.addFileToGrid(filename)

            if success:
                QMessageBox.information(self, "Upload Success", "File uploaded successfully.")
            else:
                QMessageBox.warning(self, "Upload Failed", "Error uploading file.")
        except Exception as e:
            QMessageBox.warning(self, "Upload Failed", str(e))



    def addFileToGrid(self, filename):
        fileIcon = QtGui.QIcon("file.png")
        iconLabel = QtWidgets.QLabel()
        iconLabel.setPixmap(fileIcon.pixmap(64, 64))
        iconLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        nameLabel = QtWidgets.QLabel(filename)
        nameLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        fileWidget = FileWidget(filename, self.clientSocket,self.user, self)
        self.fileWidgets.append(fileWidget)

        currentRow = self.file_count // 4
        currentColumn = self.file_count % 4

        self.gridLayout.setSpacing(2)
        self.gridLayout.addWidget(fileWidget, currentRow, currentColumn)
        self.file_count += 1

    def removeFileFromGrid(self, filename):
        for i, fileWidget in enumerate(self.fileWidgets):
            if fileWidget.filename == filename:
                self.gridLayout.removeWidget(fileWidget)
                fileWidget.deleteLater()
                self.fileWidgets.pop(i)
                self.file_count -= 1
                self.rearrangeGrid()
                break





    def rearrangeGrid(self):
        for i in reversed(range(self.gridLayout.count())):
            widget = self.gridLayout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        for i, fileWidget in enumerate(self.fileWidgets):
            currentRow = i // 4
            currentColumn = i % 4
            self.gridLayout.addWidget(fileWidget, currentRow, currentColumn)

        self.scrollAreaWidgetContents.update()


    def displayUserFiles(self):
        try:
            response = listFiles(self.clientSocket)
            if response and response != "No files uploaded.":
                fileList = response.split("\n")

                for filename in fileList:
                    print(f"  - {filename}")
                    self.addFileToGrid(filename)
            else:
                QMessageBox.information(self, "No Files", "No files uploaded.")
        except Exception as e:
            QMessageBox.warning(self, "Displaying uploaded files failed", str(e))



    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        MainWindow.setStyleSheet("background-color: rgb(90,114,114)")
        self.logOutButton.setText(_translate("MainWindow", "Log Out"))
        self.accountSettingsButton.setText(_translate("MainWindow", "Account Settings"))
        self.uploadButton.setText(_translate("MainWindow", "Upload Files"))
        self.helloLabel_2.setText(_translate("MainWindow", "TextLabel"))



    def openProfileSettings(self):
        self.profileSettings = ProfileSettingsWindow(
            self.clientSocket,
            {'username': self.username, 'password': self.password},
            self
        )
        self.profileSettings.show()
        self.hide()





