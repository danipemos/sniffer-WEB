import requests

# Crear los archivos de prueba
file_data = {
    "encrypted.txt": "This is an encrypted file.",
    ".zip.txt": "This is a zip file.",
    "a.txt": "This is a plain text file."
}

# Crear los archivos localmente
for filename, content in file_data.items():
    with open(filename, "w") as f:
        f.write(content)

# URL del endpoint de la vista upload_file
BASE_URL = "http://192.168.1.67:8000/monitorize/upload-file/"
hostname = "sniffer"

# Enviar los archivos al servidor
for filename in file_data.keys():
    with open(filename, "rb") as file:
        response = requests.post(
            f"{BASE_URL}{hostname}/",
            files={"file": file}
        )

    # Imprimir los resultados
    print(f"Testing file: {filename}")
    print(f"Response status code: {response.status_code}")
    print(f"Response JSON: {response.json()}")
    print("-" * 50)