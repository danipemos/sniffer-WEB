from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import DeviceCreationForm, PrivateKeyCreationForm
from .models import Device,File,PrivateKey
from users.forms import UserCreationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import paramiko
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json
from django.core.files.base import ContentFile
import pyzipper
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.Util.Padding import unpad
from Crypto.PublicKey import RSA
import os
import zipfile
import re


@login_required
def home(request):
    user_form = UserCreationForm()
    private_key_form = PrivateKeyCreationForm()
    device_form = DeviceCreationForm()
    return render(request, "home.html", {
        "user_form": user_form,
        "private_key_form": private_key_form,
        "device_form": device_form,
    })

@login_required
def add_user(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("monitorize:home")
        else:
            private_key_form = PrivateKeyCreationForm()
            device_form = DeviceCreationForm()
            return render(request, "home.html", {
                "user_form": form,
                "private_key_form": private_key_form,
                "device_form": device_form,
                "open_modal": "userModal",  # Indica que el modal de usuario debe estar abierto
            })
    else:
        return redirect("monitorize:home")

@login_required
def add_private_key(request):
    if request.method == "POST":
        form = PrivateKeyCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("monitorize:home")
        else:
            user_form = UserCreationForm()
            device_form = DeviceCreationForm()
            return render(request, "home.html", {
                "user_form": user_form,
                "private_key_form": form,
                "device_form": device_form,
                "open_modal": "privateKeyModal",  # Indica que el modal de clave privada debe estar abierto
            })
    else:
        return redirect("monitorize:home")

@login_required
def add_device(request):
    if request.method == "POST":
        form = DeviceCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("monitorize:home")
        else:
            user_form = UserCreationForm()
            private_key_form = PrivateKeyCreationForm()
            return render(request, "home.html", {
                "user_form": user_form,
                "private_key_form": private_key_form,
                "device_form": form,
                "open_modal": "deviceModal",  # Indica que el modal de dispositivo debe estar abierto
            })
    else:
        return redirect("monitorize:home")
    
@login_required
def ssh_terminal_view(request, hostname):
    device = get_object_or_404(Device, hostname=hostname)

    # Verificar si las credenciales existen en la sesión
    username = request.session.get(f"{hostname}_username")
    password = request.session.get(f"{hostname}_password")

    if not username or not password:
        # Si no existen, devolver una respuesta para solicitar credenciales
        return JsonResponse({"error": "missing_credentials"}, status=400)

    return render(request, "ssh_terminal.html", {"device": device, "username": username, "password": password})


@login_required
def set_credentials(request, hostname):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Verificar si el dispositivo existe
        device = get_object_or_404(Device, hostname=hostname)

        # Intentar establecer una conexión SSH
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(
                hostname=device.ip,
                username=username,
                password=password,
                timeout=10  # Tiempo de espera para la conexión
            )
            ssh_client.close()

            # Guardar credenciales en la sesión si la conexión fue exitosa
            request.session[f"{hostname}_username"] = username
            request.session[f"{hostname}_password"] = password

            return JsonResponse({"message": "Credentials set successfully."})
        except Exception as e:
            return JsonResponse({"error": f"SSH connection failed: {str(e)}"}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)

#@csrf_exempt
@login_required
def edit_file(request, hostname):
    device = get_object_or_404(Device, hostname=hostname)

    # Verificar credenciales en la sesión
    username = request.session.get(f"{hostname}_username")
    password = request.session.get(f"{hostname}_password")

    if not username or not password:
        return JsonResponse({"error": "Missing credentials"}, status=400)

    # Ruta fija del archivo
    file_path = "/home/dani/eloy"

    if request.method == "GET":
        try:
            # Conectar al dispositivo y leer el archivo
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=device.ip, username=username, password=password)

            # Usar SFTP para leer el archivo
            sftp = ssh_client.open_sftp()
            with sftp.file(file_path, "r") as remote_file:
                file_content = remote_file.read().decode()
            sftp.close()
            ssh_client.close()

            return JsonResponse({"fileContent": file_content})
        except Exception as e:
            return JsonResponse({"error": f"Failed to read file: {str(e)}"}, status=400)

    elif request.method == "POST":
        file_content = request.POST.get("fileContent")

        if not file_content:
            return JsonResponse({"error": "File content is required"}, status=400)

        try:
            # Conectar al dispositivo y guardar el archivo
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=device.ip, username=username, password=password)

            # Usar SFTP para guardar el archivo
            sftp = ssh_client.open_sftp()
            with sftp.file(file_path, "w") as remote_file:
                remote_file.write(file_content)
            sftp.close()
            ssh_client.close()

            return JsonResponse({"message": "File saved successfully."})
        except Exception as e:
            return JsonResponse({"error": f"Failed to save file: {str(e)}"}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)

@login_required
def device_list(request):
    devices = Device.objects.all()
    return render(request, "device_list.html", {"devices": devices})

@login_required
def device_detail(request, hostname):
    device = get_object_or_404(Device, hostname=hostname)

    # Verificar si las credenciales existen en la sesión
    username = request.session.get(f"{hostname}_username")
    password = request.session.get(f"{hostname}_password")

    # Si no existen credenciales, pasar una bandera al template
    missing_credentials = not username or not password

    # Obtener los archivos relacionados con el dispositivo
    encrypted_files = File.objects.filter(device=device, encryption="encrypted")
    zip_files = File.objects.filter(device=device, encryption="zip")
    decrypted_files = File.objects.filter(device=device, encryption="decrypted")
    private_keys = PrivateKey.objects.all()  # Obtener todas las claves privadas


    return render(request, "device_detail.html", {
        "device": device,
        "missing_credentials": missing_credentials,
        "encrypted_files": encrypted_files,
        "zip_files": zip_files,
        "decrypted_files": decrypted_files,
        "private_keys": private_keys,
    })

@login_required
def service_status(request, hostname):
    device = get_object_or_404(Device, hostname=hostname)

    # Verificar credenciales en la sesión
    username = request.session.get(f"{hostname}_username")
    password = request.session.get(f"{hostname}_password")

    if not username or not password:
        return JsonResponse({"error": "Missing credentials"}, status=400)

    try:
        # Conectar al dispositivo mediante SSH
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=device.ip, username=username, password=password)

        # Ejecutar el comando para verificar el estado del servicio
        stdin, stdout, stderr = ssh_client.exec_command("sudo systemctl is-active sniffer.service")
        status = stdout.read().decode().strip()
        ssh_client.close()

        if status == "active":
            return JsonResponse({"status": "active"})
        else:
            return JsonResponse({"status": "inactive"})
    except Exception as e:
        return JsonResponse({"error": f"Failed to check service status: {str(e)}"}, status=400)


@login_required
def start_service(request, hostname):
    device = get_object_or_404(Device, hostname=hostname)

    # Verificar credenciales en la sesión
    username = request.session.get(f"{hostname}_username")
    password = request.session.get(f"{hostname}_password")

    if not username or not password:
        return JsonResponse({"error": "Missing credentials"}, status=400)

    try:
        # Conectar al dispositivo mediante SSH
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=device.ip, username=username, password=password)

        # Ejecutar el comando para iniciar el servicio
        stdin, stdout, stderr = ssh_client.exec_command("sudo systemctl start sniffer.service")
        error = stderr.read().decode().strip()
        ssh_client.close()

        if error:
            return JsonResponse({"error": error}, status=400)
        return JsonResponse({"message": "Service started successfully"})
    except Exception as e:
        return JsonResponse({"error": f"Failed to start service: {str(e)}"}, status=400)


@login_required
def stop_service(request, hostname):
    device = get_object_or_404(Device, hostname=hostname)

    # Verificar credenciales en la sesión
    username = request.session.get(f"{hostname}_username")
    password = request.session.get(f"{hostname}_password")

    if not username or not password:
        return JsonResponse({"error": "Missing credentials"}, status=400)

    try:
        # Conectar al dispositivo mediante SSH
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=device.ip, username=username, password=password)

        # Ejecutar el comando para detener el servicio
        stdin, stdout, stderr = ssh_client.exec_command("sudo systemctl stop sniffer.service")
        error = stderr.read().decode().strip()
        ssh_client.close()

        if error:
            return JsonResponse({"error": error}, status=400)
        return JsonResponse({"message": "Service stopped successfully"})
    except Exception as e:
        return JsonResponse({"error": f"Failed to stop service: {str(e)}"}, status=400)

@csrf_exempt
def receive_device_stats(request, hostname):
    if request.method == "POST":
        if not Device.objects.filter(hostname=hostname).exists():
            return JsonResponse({"status": "error", "message": "Device not found"}, status=404)
        try:
            # Parsear los datos enviados desde el dispositivo
            stats = json.loads(request.body.decode("utf-8"))
            packets_per_protocol = stats.get("packets_per_protocol", [])
            total_time = stats.get("total_time", 0)
            total_megabytes = stats.get("total_megabytes", 0)
            average_bandwidth = stats.get("average_bandwidth", 0)
            sessions = stats.get("sessions", [])

            # Convertir listas a cadenas separadas por saltos de línea
            packets_per_protocol_str = "\n".join(packets_per_protocol)
            sessions_str = "\n".join(sessions)

            # Enviar estadísticas al grupo WebSocket correspondiente
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"stats_{hostname}",
                {
                    "type": "send_stats",
                    "data": {
                        "packets_per_protocol": packets_per_protocol_str,
                        "total_time": total_time,
                        "total_megabytes": total_megabytes,
                        "average_bandwidth": average_bandwidth,
                        "sessions": sessions_str,
                    },
                }
            )
            return JsonResponse({"status": "success", "message": "Stats received"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Failed to process stats: {str(e)}"}, status=400)
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

@csrf_exempt
def upload_file(request, hostname):
    if request.method == "POST":
        device = get_object_or_404(Device, hostname=hostname)
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return JsonResponse({"error": "No file provided"}, status=400)

        file_instance = File(
            name=uploaded_file.name,
            device=device,
            file=uploaded_file
        )
        file_instance.save()  # Esto notificará automáticamente al cliente

        return JsonResponse({"message": "File uploaded successfully"}, status=201)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@login_required
def decrypt_zip(request):
    if request.method == "POST":
        file_id = request.POST.get("fileId")
        password = request.POST.get("password")

        try:
            # Obtener el archivo ZIP de la base de datos
            zip_file_instance = get_object_or_404(File, id=file_id, encryption="zip")
            zip_file_path = zip_file_instance.file.path

            # Intentar abrir y extraer el archivo ZIP
            with pyzipper.AESZipFile(zip_file_path) as zf:
                zf.pwd = password.encode('utf-8')
                file_names = zf.namelist()
                extracted_file_name = file_names[0]
                extracted_file_content = zf.read(extracted_file_name)

            # Crear un nuevo File en la base de datos con el archivo extraído
            new_file_instance = File(
                name=extracted_file_name,
                device=zip_file_instance.device,
                file=ContentFile(extracted_file_content, name=extracted_file_name),
            )
            new_file_instance.save()

            # Eliminar el archivo ZIP original
            zip_file_instance.delete()

            return JsonResponse({"message": "File decrypted successfully."})
        except (pyzipper.BadZipFile, RuntimeError):
            return JsonResponse({"error": "Invalid password."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)

@login_required
def decrypt_encrypted_file(request):
    if request.method == "POST":
        file_id = request.POST.get("fileId")
        private_key_id = request.POST.get("privateKeyId")  # ID de la clave privada seleccionada

        try:
            # Obtener el archivo ZIP de la base de datos
            encrypted_file_instance = get_object_or_404(File, id=file_id, encryption="encrypted")
            zip_file_path = encrypted_file_instance.file.path

            # Obtener la clave privada de la base de datos
            private_key_instance = get_object_or_404(PrivateKey, id=private_key_id)
            private_key = RSA.import_key(private_key_instance.key.read())  # Corregido aquí

            # Extraer los archivos del ZIP
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                temp_dir = os.path.splitext(zip_file_path)[0]  # Crear un directorio temporal
                zip_ref.extractall(temp_dir)

            # Leer los archivos auxiliares
            iv_path = os.path.join(temp_dir, "iv.bin")
            encrypted_key_path = os.path.join(temp_dir, "encrypted_key.bin")
            encrypted_file_path = os.path.join(temp_dir, "encripted.pcap")

            with open(iv_path, "r") as iv_file:
                iv = bytes.fromhex(iv_file.read())

            with open(encrypted_key_path, "rb") as key_file:
                encrypted_key = key_file.read()

            # Desencriptar la clave con la clave privada
            cipher_rsa = PKCS1_v1_5.new(private_key)
            key = cipher_rsa.decrypt(encrypted_key, None)

            # Desencriptar el archivo principal
            with open(encrypted_file_path, "rb") as enc_file:
                encrypted_data = enc_file.read()

            cipher_aes = AES.new(key, AES.MODE_CBC, iv)
            decrypted_data = unpad(cipher_aes.decrypt(encrypted_data), AES.block_size)

            # Crear un nuevo archivo desencriptado en la base de datos
            match = re.search(r"_(\d{8}_\d{6})", encrypted_file_instance.name)
            timestamp = match.group(1)
            decrypted_file_name = f"capture_{timestamp}.pcap"

            new_file_instance = File(
                name=decrypted_file_name,
                device=encrypted_file_instance.device,
                file=ContentFile(decrypted_data, name=decrypted_file_name),
            )
            new_file_instance.save()

            # Eliminar el archivo ZIP original y el directorio temporal
            encrypted_file_instance.delete()
            os.remove(zip_file_path)
            for file in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file))
            os.rmdir(temp_dir)

            return JsonResponse({"message": "File decrypted successfully."})
        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)
