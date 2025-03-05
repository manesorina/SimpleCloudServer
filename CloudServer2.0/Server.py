import socket
import threading
import os
import json
import ssl
import hashlib

BASE_DIR = "uploads"
os.makedirs(BASE_DIR, exist_ok=True)

class User:
    def __init__(self, username):
        self.username = username
        self.userDir = os.path.join(BASE_DIR, username)
        os.makedirs(self.userDir, exist_ok=True)

    @staticmethod
    def hashPassword(password):
        return hashlib.sha256(password.encode()).hexdigest()

    def saveFile(self, filename, fileData):
        with open(os.path.join(self.userDir, filename), "wb") as f:
            f.write(fileData)

    def deleteFile(self, filename):
        filePath = os.path.join(self.userDir, filename)
        if os.path.exists(filePath):
            os.remove(filePath)
            return True
        return False

    def listFiles(self):
        return os.listdir(self.userDir)

def loadUsers():
    if not os.path.exists("users.json"):
        return {}
    with open("users.json") as f:
        return json.load(f)

def saveUsers(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

def registerUser(username, password):
    users = loadUsers()
    if username in users:
        return False
    users[username] = User.hashPassword(password)
    saveUsers(users)
    return True

def authenticateUser(username, password):
    users = loadUsers()
    hashedPassword = User.hashPassword(password)
    return users.get(username) == hashedPassword

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
                _, filename = command.split()
                handleUpload(clientSocket, loggedInUser, filename)
            elif command.startswith("DOWNLOAD") and loggedInUser:
                _, filename = command.split()
                handleDownload(clientSocket, loggedInUser, filename)
            elif command.startswith("LIST") and loggedInUser:
                listUserFiles(clientSocket, loggedInUser)
            elif command.startswith("DELETE") and loggedInUser:
                _, filename = command.split()
                deleteUserFile(clientSocket, loggedInUser, filename)
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

def handleUpload(clientSocket, user, filename):
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

def handleDownload(clientSocket, user, filename):
    filePath = os.path.join(user.userDir, filename)
    if not os.path.exists(filePath):
        clientSocket.send(b"ERROR: File not found.")
        return


    clientSocket.send(b"READY")
    fileSize = os.path.getsize(filePath)
    clientSocket.send(str(fileSize).encode())

    with open(filePath, "rb") as f:
        while chunk := f.read(4096):
            clientSocket.sendall(chunk)



def listUserFiles(clientSocket, user):
    files = user.listFiles()
    if files:
        clientSocket.send("\n".join(files).encode())
    else:
        clientSocket.send(b"No files uploaded.")

def deleteUserFile(clientSocket, user, filename):
    if user.deleteFile(filename):
        clientSocket.send(b"DELETE_SUCCESS")
    else:
        clientSocket.send(b"ERROR: File not found.")

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