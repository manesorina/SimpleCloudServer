import os.path

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QAction

from ProfileSettingsScreen import ProfileSettingsWindow
from Client import uploadFile,deleteFile
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QMenu


from FileWidget import FileWidget



class ProfileWindow(QMainWindow):
    def __init__(self,clientSocket,user):
        super().__init__()
        self.clientSocket=clientSocket
        self.user=user
        self.setupUi(self)
        self.file_count=0





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
        self.accountSettingsButton.clicked.connect(self.goToProfileSettings)

        self.scrollArea = QtWidgets.QScrollArea(parent=self.centralwidget)
        self.scrollArea.setGeometry(QtCore.QRect(20, 220, 761, 341))
        self.scrollArea.setWidgetResizable(True)  # Allow the widget to resize
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
        fileWidget = FileWidget(filename, self.clientSocket, self)

        currentRow = self.file_count // 4
        currentColumn = self.file_count % 4

        self.gridLayout.setSpacing(2)
        self.gridLayout.addWidget(fileWidget, currentRow, currentColumn)
        self.file_count += 1

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        MainWindow.setStyleSheet("background-color: rgb(90,114,114)")
        self.logOutButton.setText(_translate("MainWindow", "Log Out"))
        self.accountSettingsButton.setText(_translate("MainWindow", "Account Settings"))
        self.uploadButton.setText(_translate("MainWindow", "Upload Files"))
        self.helloLabel_2.setText(_translate("MainWindow", "TextLabel"))


    def goToProfileSettings(self):
        self.profileSettingsWindow=ProfileSettingsWindow(self.clientSocket,self.user)
        self.profileSettingsWindow.show()
        self.mainWindow.close()




