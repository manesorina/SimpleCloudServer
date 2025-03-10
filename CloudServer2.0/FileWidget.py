from __future__ import annotations
import os
from typing import TYPE_CHECKING

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QMenu, QProgressDialog
from PyQt6 import QtCore, QtGui, QtWidgets
from Client import downloadFile, deleteFile


if TYPE_CHECKING:
    from ProfileScreen import ProfileWindow


class FileWidget(QtWidgets.QWidget):
    def __init__(self, filename,clientSocket,username, parent: 'ProfileWindow' = None):
        super().__init__(parent)
        self.filename = filename
        self.clientSocket = clientSocket
        self.username = username
        self.parent: ProfileWindow = parent
        self.setFixedSize(150,130)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)


        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.iconLabel = QtWidgets.QLabel()
        fileIcon = QtGui.QIcon("file.png")
        self.iconLabel.setPixmap(fileIcon.pixmap(64, 64))
        self.iconLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)


        self.nameLabel = QtWidgets.QLabel(filename)
        self.nameLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.layout.addWidget(self.iconLabel)
        self.layout.addWidget(self.nameLabel)

        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

    def showContextMenu(self, pos):
        menu = QMenu(self)

        menu.setStyleSheet("""
                    QMenu {
                        background-color: rgb(50, 70, 70);  /* Background color */
                        border: 1px solid rgb(100, 150, 150);
                    }
                    QMenu::item {
                        font-size: 16px;  /* Bigger text */
                        padding: 10px 20px;  /* More spacing */
                        color: white;  /* White text */
                    }
                    QMenu::item:selected {
                        background-color: rgb(80, 100, 100); /* Highlight color */
                    }
                """)

        download_action = QAction("⬇ Download", self)
        delete_action = QAction("🗑 Delete", self)

        download_action.triggered.connect(self.downloadFile)
        delete_action.triggered.connect(self.deleteFile)

        menu.addAction(download_action)
        menu.addAction(delete_action)

        menu.exec(self.mapToGlobal(pos))



    def downloadFile(self):
        savePath, _ = QFileDialog.getSaveFileName(self, "Save File", self.filename)
        if not savePath:
            return
        try:
            filename = os.path.basename(self.filename)
            success = downloadFile(self.clientSocket, filename, savePath)

            if success:
                QMessageBox.information(self, "Download Success", "File downloaded successfully.")
            else:
                QMessageBox.warning(self, "Download Failed", "Error downloading the file.")

        except Exception as e:
            QMessageBox.warning(self, "Download Failed", str(e))


    def deleteFile(self):
        confirm = QMessageBox.question(self, "Confirm Deletion", f"Are you sure you want to delete {self.filename}?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirm == QMessageBox.StandardButton.Yes:

            success = deleteFile(self.clientSocket, self.filename)
            if success:
                if self.parent is not None:
                    self.parent.removeFileFromGrid(self.filename)
                    QMessageBox.information(self.parent, "File Deleted", f"{self.filename} has been deleted.")

            else:
                QMessageBox.warning(self.parent, "Deletion Failed", "Could not delete the file.")




