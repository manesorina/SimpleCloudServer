import socket
import threading
import os
import json
import ssl
import hashlib
import urllib.parse

BASE_DIR = "/home/so17/CloudServer2.0/uploads"
os.makedirs(BASE_DIR, exist_ok=True)


class User:
    """
    User class to manage user-specific operations and data

    Attributes:
        username (str): The user's unique identifier
        userDir (str): Path to the user's file directory
    """

    def __init__(self, username):
        """Initialize a user with a username and create their directory"""
        self.username = username
        self.userDir = os.path.join(BASE_DIR, username)
        os.makedirs(self.userDir, exist_ok=True)

    @staticmethod
    def hashPassword(password):
        """
        Hash a password using SHA-256

        Args:
            password (str): The password to hash

        Returns:
            str: The hexadecimal digest of the hashed password
        """
        try:
            return hashlib.sha256(password.encode()).hexdigest()
        except Exception as e:
            print(f"[ERROR] Hashing password failed: {e}")

    def saveFile(self, filename, fileData):
        """
        Save file data to the user's directory

        Args:
            filename (str): Name of the file to save
            fileData (bytes): Binary data of the file
        """
        try:
            with open(os.path.join(self.userDir, filename), "wb") as f:
                f.write(fileData)
        except Exception as e:
            print(f"[ERROR] Failed to save the file {filename}: {e}")

    def deleteFile(self, filename):
        """
        Delete a file from the user's directory

        Args:
            filename (str): Name of the file to delete

        Returns:
            bool: True if file was deleted, False if file not found
        """

        try:
            filePath = os.path.join(self.userDir, filename)
            if os.path.exists(filePath):
                os.remove(filePath)
                return True
            return False
        except Exception as e:
            print(f"[ERROR] Failed to delete file {filename}: {e}")
            return False

    def listFiles(self):
        """
        List all files in the user's directory

        Returns:
            list: List of filenames in the user's directory
        """
        return os.listdir(self.userDir)




def loadUsers():
    """
    Load user data from users.json file

    Returns:
        dict: Dictionary of username to hashed password mappings
    """
    try:
        if not os.path.exists("users.json"):
            return {}
        with open("users.json") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load users: {e}")
        return {}



def saveUsers(users):
    """
    Save user data to users.json file

    Args:
        users (dict): Dictionary of username to hashed password mappings
    """
    try:
        with open("users.json", "w") as f:
            json.dump(users, f)
    except Exception as e:
        print(f"[ERROR] Failed to save users: {e}")


def registerUser(username, password):
    """
    Register a new user

    Args:
        username (str): Username for the new user
        password (str): Password for the new user

    Returns:
        bool: True if registration successful, False if username already exists
    """
    try:
        users = loadUsers()
        if username in users:
            return False
        users[username] = User.hashPassword(password)
        saveUsers(users)
        return True
    except Exception as e:
        print(f"[ERROR] Registration failed: {e}")
        return False


def authenticateUser(username, password):
    """
    Authenticate a user with username and password

    Args:
        username (str): Username to authenticate
        password (str): Password to verify

    Returns:
        bool: True if authentication successful, False otherwise
    """
    try:
        users = loadUsers()
        hashedPassword = User.hashPassword(password)
        return users.get(username) == hashedPassword
    except Exception as e:
        print(f"[ERROR] Authentication failed: {e}")
        return False






"""
    Handle client connection and process commands

    This function runs in a separate thread for each client connection.
    It processes commands received from the client and calls appropriate
    functions to handle each command.

    Args:
        clientSocket (socket): Socket object for client communication
    """
def handleClient(clientSocket):
    loggedInUser = None
    try:
        while True:
            command = clientSocket.recv(1024).decode()
            if not command:
                break

            if command.startswith("REGISTER"):
                _, username, password = command.split()
                if registerUser(username, password):
                    clientSocket.send(b"Registration successful.")
                else:
                    clientSocket.send(b"User already exists.")

            elif command.startswith("LOGIN"):
                _, username, password = command.split()
                if authenticateUser(username, password):
                    loggedInUser = User(username)
                    clientSocket.send(b"Login successful.")
                else:
                    clientSocket.send(b"Invalid credentials.")


            elif command.startswith("UPLOAD") and loggedInUser:
                parts = command.split(" ", 1)
                if len(parts) > 1:
                    encoded_filename = parts[1]
                    filename = urllib.parse.unquote(encoded_filename)
                    handleUpload(clientSocket, loggedInUser, filename)


            elif command.startswith("DOWNLOAD") and loggedInUser:
                parts = command.split(" ", 1)
                if len(parts) > 1:
                    encoded_filename = parts[1]
                    filename = urllib.parse.unquote(encoded_filename)
                    handleDownload(clientSocket, loggedInUser, filename)



            elif command.startswith("LIST") and loggedInUser:
                listUserFiles(clientSocket,loggedInUser)


            elif command.startswith("DELETE") and loggedInUser:
                parts = command.split(" ", 1)
                if len(parts) > 1:
                    encoded_filename = parts[1]
                    filename = urllib.parse.unquote(encoded_filename)
                    deleteUserFile(clientSocket, loggedInUser, filename)


            elif command.startswith("CHANGE_USERNAME") and loggedInUser:
                _, newUsername = command.split(maxsplit=1)
                if changeUserUsername(loggedInUser.username, newUsername):
                    loggedInUser.username = newUsername  # Update the logged-in user
                    clientSocket.send(b"USERNAME_CHANGED")
                else:
                    clientSocket.send(b"ERROR: Username already taken.")

            elif command.startswith("CHANGE_PASSWORD") and loggedInUser:
                _, newPassword = command.split(maxsplit=1)
                if changeUserPassword(loggedInUser.username, newPassword):
                    clientSocket.send(b"PASSWORD_CHANGED")
                else:
                    clientSocket.send(b"ERROR: Password change failed.")


            elif command.startswith("DELETE_ACCOUNT") and loggedInUser:
                if deleteUser(loggedInUser.username):
                    clientSocket.send(b"ACCOUNT_DELETED")
                    break
                else:
                    clientSocket.send(b"ERROR: Account deletion failed.")

            elif command == "EXIT":
                clientSocket.close()
                break
            else:
                clientSocket.send(b"ERROR: Invalid command or not logged in.")

    except Exception as e:
        print(f"[ERROR] {e}")

    finally:
        print(f"[INFO] Client disconnected")
        clientSocket.close()




"""
    Handle file upload from client

    Process:
    1. Receive file size from client
    2. Send READY signal to client
    3. Receive file data from client
    4. Save file to user's directory
    5. Send success message to client

    Args:
        clientSocket (socket): Socket object for client communication
        user (User): User object for the logged in user
        filename (str): Name of the file to upload
    """


def handleUpload(clientSocket, user, filename):
    try:
        fileSizeData = clientSocket.recv(1024).decode().strip()
        if not fileSizeData.isdigit():
            print(f"[ERROR] Invalid file size received: {fileSizeData}")
            return
        fileSize = int(fileSizeData)
        clientSocket.send(b"READY")

        fileData = b""
        while len(fileData) < fileSize:
            chunk = clientSocket.recv(4096)
            if not chunk:
                break
            fileData += chunk

        user.saveFile(filename, fileData)
        clientSocket.send(b"UPLOAD_SUCCESS")
    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")


"""
    Handle file download to client

    Process:
    1. Check if file exists
    2. Send READY signal to client
    3. Send file size to client
    4. Send file data to client

    Args:
        clientSocket (socket): Socket object for client communication
        user (User): User object for the logged in user
        filename (str): Name of the file to download
    """


def handleDownload(clientSocket, user, filename):
    try:
        filePath = os.path.join(user.userDir, filename)

        if not os.path.exists(filePath):
            clientSocket.send(b"ERROR: File not found.")
            return


        clientSocket.send(b"READY")

        ack = clientSocket.recv(1024).decode().strip()
        if ack != "ACK":
            print(f"[ERROR] Client didn't acknowledge READY signal: {ack}")
            return

        fileSize = os.path.getsize(filePath)
        clientSocket.send(str(fileSize).encode())

        size_ack = clientSocket.recv(1024).decode().strip()
        if size_ack != "SIZE_ACK":
            print(f"[ERROR] Client didn't acknowledge file size: {size_ack}")
            return

        with open(filePath, "rb") as f:
            while chunk := f.read(1024):
                clientSocket.sendall(chunk)
        print(f"[INFO] File {filename} successfully sent to {user.username}")
    except Exception as e:
        print(f"[ERROR] Download failed: {e}")






"""
    List files for a user and send to client

    Args:
        clientSocket (socket): Socket object for client communication
        user (User): User object for the logged in user
    """
def listUserFiles(clientSocket, user):
    files = user.listFiles()
    if files:
        clientSocket.send("\n".join(files).encode())
    else:
        clientSocket.send(b"No files uploaded.")





"""
    Delete a user file

    Args:
        clientSocket (socket): Socket object for client communication
        user (User): User object for the logged in user
        filename (str): Name of the file to delete
    """
def deleteUserFile(clientSocket, user, filename):
    try:
        response = b"DELETE_SUCCESS" if user.deleteFile(filename) else b"ERROR: File not found."
        clientSocket.send(response)
    except Exception as e:
        print(f"[ERROR] Deleting file failed: {e}")




"""
    Change a user's username.

    Args:
        oldUsername (str): The current username.
        newUsername (str): The new username to assign.

    Returns:
        bool: True if the username was changed successfully, False if the new username already exists.
    """
def changeUserUsername(oldUsername, newUsername):
    try:
        users = loadUsers()
        if newUsername in users:
            return False

        users[newUsername] = users.pop(oldUsername)
        os.rename(os.path.join(BASE_DIR, oldUsername), os.path.join(BASE_DIR, newUsername))
        saveUsers(users)
        return True
    except Exception as e:
        print(f"Error changing user's : {oldUsername} username: {str(e)}")
        return False






"""
    Change a user's password.

    Args:
        username (str): The username whose password will be changed.
        newPassword (str): The new password.

    Returns:
        bool: True if the password was updated successfully, False if the user does not exist.
    """
def changeUserPassword(username, newPassword):
    try:
        users = loadUsers()
        if username not in users:
            return False

        users[username] = User.hashPassword(newPassword)
        saveUsers(users)
        return True
    except Exception as e:
        print(f"Error changing user's: {username} password: {str(e)}")
        return False


"""
    Delete a user from the system.

    Args:
        username (str): The username of the user to delete.

    Returns:
        bool: True if the user was deleted successfully, False if the user does not exist or an error occurs.
    """
def deleteUser(username):
    try:
        users = loadUsers()
        if username in users:
            del users[username]
            saveUsers(users)


            userDir = os.path.join(BASE_DIR, username)
            if os.path.exists(userDir):
                import shutil
                shutil.rmtree(userDir)
            return True
        return True
    except Exception as e:
        print(f"Error deleting user {username}: {str(e)}")
        return False




"""
    Start the server and listen for client connections

    This function:
    1. Creates a socket
    2. Binds to port 5000
    3. Sets up SSL/TLS
    4. Listens for client connections
    5. Creates a new thread for each client
    """
def startServer():
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind(("0.0.0.0", 5000))
    serverSocket.listen(5)
    print("[INFO] Server listening on port 5000 with SSL/TLS")

    context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

    try:

        while True:
            clientSocket, _ = serverSocket.accept()
            clientThread = threading.Thread(target=handleClient, args=(clientSocket,))
            clientThread.start()
    except KeyboardInterrupt:
        print("\n[INFO] Closing server.")
    finally:
        serverSocket.close()
        print("\n[INFO] Server closed.")




if __name__ == "__main__":
    startServer()