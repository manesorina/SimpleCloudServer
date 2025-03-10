# SimpleCloudServer

## Overview
SimpleCloudServer is a lightweight cloud storage system that enables users to register, log in, upload, download, list, and delete files through a client-server architecture using Python sockets. 

## Features
- **User  Authentication**: Register, log in, change username, and change password.
- **File Management**: Upload, download, list, and delete files.
- **Secure Password Storage**: Utilizes SHA-256 hashing for secure password management.
- **Multi-threaded Server**: Capable of handling multiple clients simultaneously.
- **Error Handling**: Basic error handling and response validation to enhance user experience.

## Technologies Used
- **Python 3**: The primary programming language.
- **Sockets**: For client-server communication.
- **JSON**: For user management.
- **OS**: For file operations.
- **Hashlib**: For password hashing.
- **Urllib.parse**: For safe filename transmission.
- **PyQT6**: For the user interface.

## Installation and Setup

### Prerequisites
- Python 3.11 installed on both the server and client machines.
- SSL certificate (`cert.pem`) and private key (`key.pem`) files for secure communication.

### Installation Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/cloud-server.git
   cd cloud-server
   ```

2. Generate SSL Certificate and Private Key:

  Generate the Private Key
  ```bash
  openssl genpkey -algorithm RSA -out key.pem -aes256
  ```

  Generate the Certificate:
  ```bash
  openssl req -new -x509 -key key.pem -out cert.pem -days 365
  ```
  This command creates a self-signed SSL certificate valid for 365 days. You will be prompted to enter details such as country name and organization name.

3. Place both cert.pem and key.pem files in the root directory of your project.

### Running the application
1. Start the server:
  ```bash
   python3 server.py
  ```
2.In a separate terminal or machine, run the client:
  ```bash
   python3 client.py
  ```

  

