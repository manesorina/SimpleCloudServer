import socket
import os
import ssl
import sys

from PyQt6.QtWidgets import QApplication



def registerUser(clientSocket,username,password):
    clientSocket.send(f"REGISTER {username} {password}".encode())
    return clientSocket.recv(1024).decode()


def loginUser(clientSocket,username,password):
    clientSocket.send(f"LOGIN {username} {password}".encode())
    response = clientSocket.recv(1024).decode()
    return response == "Login successful.", response




def uploadFile(clientSocket, filePath):
    filename = os.path.basename(filePath)
    if not os.path.exists(filePath):
        print(f"[ERROR] File not found: {filePath}")
        return False

    try:
        clientSocket.send(f"UPLOAD {filename}".encode())
        fileSize = os.path.getsize(filePath)
        clientSocket.send(str(fileSize).encode())

        response = clientSocket.recv(1024).decode()
        if response != "READY":
            print(f"[ERROR] Unexpected server response: {response}")
            return False

        with open(filePath, "rb") as f:
            while chunk := f.read(4096):
                clientSocket.sendall(chunk)

        final_response = clientSocket.recv(1024).decode()
        if final_response == "UPLOAD_SUCCESS":
            print("[DEBUG] File uploaded successfully.")
            return True
        else:
            print(f"[ERROR] Upload failed, server response: {final_response}")
            return False

    except (socket.error, ConnectionError) as e:
        print(f"[ERROR] Network error: {e}")
        return False

    except IOError as e:
        print(f"[ERROR] File reading error: {e}")
        return False

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False




def downloadFile(clientSocket, filePath):
    try:
        clientSocket.send(f"DOWNLOAD {filePath}".encode())
        response = clientSocket.recv(1024).decode().strip()

        if response.startswith("ERROR"):
            print(f"[ERROR] Server responded with: {response}")
            return False

        if not response.startswith("READY"):
            print(f"[ERROR] Unexpected server response: {response}")
            return False

        fileSizeData = clientSocket.recv(1024).decode().strip()
        if not fileSizeData.isdigit():
            return False

        fileSize = int(fileSizeData)

        with open(filePath, "wb") as f:
            bytesReceived = 0
            while bytesReceived < fileSize:
                fileData = clientSocket.recv(4096)
                if not fileData:
                    raise ConnectionError("Connection lost during file transfer.")
                f.write(fileData)
                bytesReceived += len(fileData)

        return True

    except (socket.error, ConnectionError) as e:
        print(f"[ERROR] Network error: {e}")
        return False

    except IOError as e:
        print(f"[ERROR] File writing error: {e}")
        return False

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False




def listFiles(clientSocket):
    clientSocket.send(b"LIST")
    print(clientSocket.recv(4096).decode())




def deleteFile(clientSocket, filename, username):
    try:

        if clientSocket is None:
            print("[ERROR] Client socket is not initialized.")
            return False


        clientSocket.send(f"DELETE {username} {filename}".encode())
        response = clientSocket.recv(1024).decode().strip()

        if response == "DELETE_SUCCESS":
            print("[DEBUG] File deleted successfully.")
            return True
        else:
            print(f"[ERROR] Server response: {response}")
            return False

    except (socket.error, ConnectionError) as e:
        print(f"[ERROR] Network error: {e}")
        return False

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False








