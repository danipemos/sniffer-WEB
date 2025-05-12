# Titulo

## Description
Web application based on Django to monitor "nombre sniffer", a service that captures and manages network data with a focus on data protection, security, and privacy.

## Key Features
- User management system: Allows the creation and management of users authorized to access the web application.
- GPG key management: Enables the creation and management of GPG keys used to encrypt the captured files.
- Device management system to monitor the service execution, including:
  - Editing the config.ini file
  - Opening an SSH terminal to the device
  - Starting and stopping the sniffer.service
  - Viewing real-time execution statistics
  - Receiving, decrypting, and downloading captured files
  - Sending the public GPG key to the device and adding it to the keyring

## Instalation
1. Clone the repository
   ```bash
   poner link
   cd carpeta
2. Go to the .devcontainer folder and create the docker containers with docker compose:
    ```bash
    docker compose up -d --build

## LICENSE
GNU General Public License v3.0 or later. See the [LICENSE](LICENSE) file for details.
