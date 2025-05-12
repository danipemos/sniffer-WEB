# Titulo

## Description
Aplication web based on django to monitorize "nombre sniffer" a service that captures and manages network data remotely

## Key Features
- User management system that allows for the creation and management of users who are authorized to access the web application.
- GPG management system that allows for the creation and management of the gpg keys used to cypher the captures files.
- Device magement system to monitorize the execution of the service, it includes:
  - Modification of the config.ini file
  - Open a ssh termial to the device
  - Start and stop the sniffer.service
  - View in real time the stadistics of the execution of the service.
  - Recive, decrypt and download the captured files.
  - Send the public gpg key to the device and add it to the ring.

## Instalation
1. Clone the repository
   ```bash
   poner link
   cd carpeta
2. Go to the .devcontainer folder and create the docker containers with docker compose:
    ```bash
    docker compose docker-compose.yml
3. Open a terminal in the docker container

## LICENSE
GNU General Public License v3.0 or later. See the [LICENSE](LICENSE) file for details.
