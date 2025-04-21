import requests
import json
import time
import random

# URL del endpoint (ajusta el hostname y puerto según tu configuración)
url = "http://192.168.1.67:8000/monitorize/api/stats/sniffer/"

# Función para generar datos simulados dinámicos
def generate_data():
    return {
        "packets_per_protocol": random.sample(["TCP", "UDP", "ICMP", "HTTP", "HTTPS"], random.randint(1, 5)),
        "total_time": random.randint(1, 3600),  # Tiempo total en segundos
        "total_megabytes": round(random.uniform(50.0, 500.0), 2),  # Megabytes totales
        "average_bandwidth": round(random.uniform(1.0, 100.0), 2),  # Ancho de banda promedio en Mbps
        "sessions": [f"Session{random.randint(1, 100)}" for _ in range(random.randint(1, 5))]
    }

# Enviar datos cada segundo
try:
    while True:
        data = generate_data()
        response = requests.post(url, data=json.dumps(data), headers={"Content-Type": "application/json"})
        print("Status Code:", response.status_code)
        print("Response JSON:", response.json())
        time.sleep(1)  # Esperar 1 segundo antes de enviar el siguiente conjunto de datos
except KeyboardInterrupt:
    print("Detenido por el usuario.")
except Exception as e:
    print("Error:", str(e))