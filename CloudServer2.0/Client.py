import socket
import os
import urllib.parse



"""
    Register a new user.

    Args:
        clientSocket (socket): The socket object for server communication.
        username (str): The desired username.
        password (str): The user's password.

    Returns:
        tuple: (bool, str) indicating success status and server response message.
    """
def registerUser(clientSocket,username,password):
    try:
        clientSocket.send(f"REGISTER {username} {password}".encode())
        return clientSocket.recv(1024).decode()
    except (socket.error, ConnectionError) as e:
        print(f"[ERROR] Network error: {e}")
        return False

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False



"""
    Log in an existing user.

    Args:
        clientSocket (socket): The socket object for server communication.
        username (str): The user's username.
        password (str): The user's password.

    Returns:
        tuple: (bool, str) indicating success status and server response message.
    """
def loginUser(clientSocket,username,password):
    try:
        clientSocket.send(f"LOGIN {username} {password}".encode())
        response = clientSocket.recv(1024).decode()
        return response == "Login successful.", response
    except (socket.error, ConnectionError) as e:
        print(f"[ERROR] Network error: {e}")
        return False

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False



"""
    Upload a file to the server.

    Args:
        clientSocket (socket): The socket object for server communication.
        filePath (str): The local path of the file to be uploaded.

    Returns:
        bool: True if upload is successful, False otherwise.
    """
def uploadFile(clientSocket, filePath):
    filename = os.path.basename(filePath)
    encoded_filename = urllib.parse.quote(filename)
    if not os.path.exists(filePath):
        print(f"[ERROR] File not found: {filePath}")
        return False

    try:
        clientSocket.send(f"UPLOAD {encoded_filename}".encode())
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




"""
    Download a file from the server.

    Args:
        clientSocket (socket): The socket object for server communication.
        filename (str): The name of the file to be downloaded.
        savePath (str): The local path where the file should be saved.

    Returns:
        bool: True if download is successful, False otherwise.
    """
def downloadFile(clientSocket, filename, savePath):
    try:
        encoded_filename=urllib.parse.quote(filename)
        clientSocket.send(f"DOWNLOAD {encoded_filename}".encode())
        response = clientSocket.recv(1024).decode().strip()

        if response.startswith("ERROR"):
            print(f"[ERROR] Server responded with: {response}")
            return False

        if not response.startswith("READY"):
            print(f"[ERROR] Unexpected server response: {response}")
            return False

        clientSocket.send(b"ACK")
        fileSizeData = clientSocket.recv(1024).decode().strip()
        if not fileSizeData.isdigit():
            print(f"[ERROR] Invalid file size received: {fileSizeData}")
            return False
        clientSocket.send(b"SIZE_ACK")

        fileSize = int(fileSizeData)
        print(f"[INFO] Downloading {filename} ({fileSize} bytes) to {savePath}")

        with open(savePath, "wb") as f:
            bytesReceived = 0
            while bytesReceived < fileSize:
                fileData = clientSocket.recv(1024)
                if not fileData:
                    raise ConnectionError("Connection lost during file transfer.")
                f.write(fileData)
                bytesReceived += len(fileData)
                print(f"\rProgress: {bytesReceived}/{fileSize} bytes ({(bytesReceived / fileSize) * 100:.1f}%)", end="")

        print("\n[INFO] Download complete!")
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



"""
    Retrieve the list of files from the server.

    Args:
        clientSocket (socket): The socket object for server communication.

    Returns:
        tuple: (bool, str) indicating success status and server response message.    
    """
def listFiles(clientSocket):
    try:
        clientSocket.send(b"LIST")
        return clientSocket.recv(4096).decode()
    except Exception as e:
        print(f"[ERROR] Unexpected error in listFiles: {e}")
        return False


"""
    Delete a file from the server.

    Args:
        clientSocket (socket): The socket object for server communication.
        filename (str): The name of the file to be deleted.

    Returns:
        bool: True if deletion is successful, False otherwise.
    """
def deleteFile(clientSocket,filename):
    encoded_filename=urllib.parse.quote(filename)
    try:
        clientSocket.send(f"DELETE {encoded_filename}".encode())
        response=clientSocket.recv(1024).decode()
        return response.strip()== "DELETE_SUCCESS",response.strip()

    except (socket.error, ConnectionError) as e:
        print(f"[ERROR] Network error: {e}")
        return False

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False



"""
    Change the username of the logged-in user.

    Args:
        clientSocket (socket): The socket object for server communication.
        newUsername (str): The new username to be assigned.

    Returns:
        bool: True if username change is successful, False otherwise.
    """
def changeUsername(clientSocket, newUsername):
    try:
        clientSocket.send(f"CHANGE_USERNAME {newUsername}".encode())
        response = clientSocket.recv(1024).decode()
        return response == "USERNAME_CHANGED"
    except (socket.error, ConnectionError) as e:
        print(f"[ERROR] Network error: {e}")
        return False

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False




"""
    Change the password of the logged-in user.

    Args:
        clientSocket (socket): The socket object for server communication.
        newPassword (str): The new password to be set.

    Returns:
        bool: True if password change is successful, False otherwise.
    """
def changePassword(clientSocket, newPassword):
    try:
        clientSocket.send(f"CHANGE_PASSWORD {newPassword}".encode())
        response = clientSocket.recv(1024).decode()
        return response == "PASSWORD_CHANGED"
    except (socket.error, ConnectionError) as e:
        print(f"[ERROR] Network error: {e}")
        return False

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False



"""
    Delete the logged-in user's account.

    Args:
        clientSocket (socket): The socket object for server communication.

    Returns:
        bool: True if account deletion is successful, False otherwise.
    """
def deleteAccount(clientSocket):
    clientSocket.send(b"DELETE_ACCOUNT")
    response = clientSocket.recv(1024).decode()
    return response == "ACCOUNT_DELETED"







