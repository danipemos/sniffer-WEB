from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import DeviceCreationForm, PrivateKeyCreationForm, DeviceChangeForm
from .models import Device,File
from users.forms import UserCreationForm, UserChangeForm
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
from django.contrib.auth import get_user_model
import gnupg
from django.conf import settings
from datetime import datetime
from django.http import HttpResponse
gpg = gnupg.GPG(gnupghome=settings.GNUPG_HOME)


User = get_user_model()

@login_required
def home(request):
    return render(request, "home.html")

@login_required
def add_user(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"message": "User added successfully."})
        else:
            return JsonResponse({"errors": form.errors}, status=400)
    return redirect("monitorize:users")

@login_required
def add_private_key(request):
    if request.method == "POST":
        form = PrivateKeyCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"message": "Private key added successfully."})
        else:
            return JsonResponse({"errors": form.errors}, status=400)
    return redirect("monitorize:private_keys")

@login_required
def add_device(request):
    if request.method == "POST":
        form = DeviceCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"message": "Device added successfully."})
        else:
            return JsonResponse({"errors": form.errors}, status=400)
    else:
        return redirect("monitorize:devices")
    
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
    file_path = "/home/dani/sniffer/config.ini"

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
    devices = Device.objects.all().order_by("id")
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
    private_keys = []  # Obtener todas las claves privadas
    for key in gpg.list_keys():       
        private_keys.append({
            'real_name': key['uids'][0].split('<')[0].strip(),
            'keyid': key['keyid'],
            'email': key['uids'][0].split('<')[1].strip('>'),
            'fingerprint': key['fingerprint'],
        })

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
            elapsed_time = stats.get("elapsed_time", 0)
            total_packets = stats.get("total_packets", {})
            total_megabytes = stats.get("total_megabytes", 0)
            bandwidth_mbps = stats.get("bandwidth_mbps", 0)
            sessions = stats.get("sessions", [])
            processing_packets = stats.get("processing_packets", None)  # Campo opcional

            # Convertir el diccionario de paquetes por protocolo a una cadena legible
            packets_per_protocol_str = "\n".join(
                f"{protocol}: {count}" for protocol, count in total_packets.items()
            )

            # Convertir las sesiones a una cadena legible
            sessions_str = "\n".join(
                f"{session['protocol']} {session['src_ip']}{session['src_port']} -> {session['dst_ip']}{session['dst_port']} "
                f"Packets: {session['packet_count']} Size: {session['total_size_kb']} KB"
                for session in sessions
            )

            # Enviar estadísticas al grupo WebSocket correspondiente
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"stats_{hostname}",
                {
                    "type": "send_stats",
                    "data": {
                        "packets_per_protocol": packets_per_protocol_str,
                        "total_time": elapsed_time,
                        "total_megabytes": total_megabytes,
                        "average_bandwidth": bandwidth_mbps,
                        "sessions": sessions_str,
                        "processing_packets": processing_packets,  # Incluir el campo opcional
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
        passphrase = request.POST.get("passphrase")  # ID de la clave privada seleccionada

        try:
            # Obtener el archivo ZIP de la base de datos
            encrypted_file_instance = get_object_or_404(File, id=file_id, encryption="encrypted")
            file_path = encrypted_file_instance.file.path
            match = re.search(r"_(\d{8}_\d{6})", encrypted_file_instance.name)
            timestamp = match.group(1)
            decrypted_file_name = f"capture_{timestamp}.pcap"
            with open(file_path, "rb") as f:
                state=gpg.decrypt_file(f, passphrase=passphrase)
                if not state.ok:
                    return JsonResponse({"error": "Decryption failed. Check the passphrase"}, status=400)

            # Crear un nuevo archivo desencriptado en la base de datos

            new_file_instance = File(
                name=decrypted_file_name,
                device=encrypted_file_instance.device,
                file=ContentFile(state.data, name=decrypted_file_name),
            )
            new_file_instance.save()

             # Eliminar el archivo GPG original
            encrypted_file_instance.delete()

            return JsonResponse({"message": "File decrypted successfully."})
        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)

@login_required
def users(request):
    users = User.objects.all().order_by("id") 
    return render(request, "users.html", {"users": users})

@login_required
def private_keys(request):
    private_keys = []
    for key in gpg.list_keys():
        # Mapear el algoritmo a un nombre legible
        algorithm = "RSA" if key['algo'] == "1" else "DSA" if key['algo'] == "2" else "Unknown"

        # Obtener la fecha de expiración
        expires = key.get('expires')
        expiration_date = (
            datetime.utcfromtimestamp(int(expires)).strftime('%Y-%m-%d') if expires else "No expiration"
        )
        
        private_keys.append({
            'real_name': key['uids'][0].split('<')[0].strip(),
            'keyid': key['keyid'],
            'email': key['uids'][0].split('<')[1].strip('>'),
            'algorithm': algorithm,
            'key_size': key['length'],
            'expiration_date': expiration_date,
            'fingerprint': key['fingerprint'],
        })
    return render(request, "private_keys.html", {"private_keys": private_keys})


@login_required
def delete_private_key(request, key_id):
    if request.method == "POST":
        passphrase = request.POST.get("passphrase")  # Obtener el passphrase del formulario
        if not passphrase:
            return JsonResponse({"error": "Passphrase is required."}, status=400)

        # Intentar eliminar la clave privada
        result_private = gpg.delete_keys(key_id, True,expect_passphrase=False)
        if result_private.status != "ok":
            return JsonResponse({"error": f"Failed to delete private key: {result_private.stderr}"}, status=400)

        # Intentar eliminar la clave pública
        result_public = gpg.delete_keys(key_id, False)
        if result_public.status != "ok":
            return JsonResponse({"error": f"Failed to delete public key: {result_public.stderr}"}, status=400)

        return JsonResponse({"message": "Private key deleted successfully."})

    return redirect("monitorize:private_keys")

@login_required
def export_public_key(request, key_id):
    # Exportar la clave pública
    public_key = gpg.export_keys(key_id)
    if not public_key:
        return JsonResponse({"error": "Failed to export public key."}, status=400)

    # Crear una respuesta para descargar el archivo
    keys = gpg.list_keys()
    key_details = next((key for key in keys if key["fingerprint"] == key_id), None)
    keyid = key_details["keyid"]
    uid = key_details["uids"][0].replace(" ", "_").replace("<", "").replace(">", "")
    response = JsonResponse({"error": "Failed to export public key."}, status=400)
    response = HttpResponse(public_key, content_type="application/pgp-keys")
    response["Content-Disposition"] = f"attachment; filename=public_key_{keyid}_{uid}.asc"

    return response

@login_required
def import_gpg_key_to_device(request, hostname, key_id):
    if request.method == "POST":
        device = get_object_or_404(Device, hostname=hostname)

        # Verificar credenciales en la sesión
        username = request.session.get(f"{hostname}_username")
        password = request.session.get(f"{hostname}_password")

        if not username or not password:
            return JsonResponse({"error": "Missing credentials"}, status=400)

        try:
            # Exportar la clave pública
            public_key = gpg.export_keys(key_id)
            if not public_key:
                return JsonResponse({"error": "Failed to export the public key"}, status=400)

            # Conectar al dispositivo mediante SSH
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=device.ip, username=username, password=password)

            # Crear un archivo temporal con la clave pública
            temp_key_file = f"/tmp/pubkey_{key_id}.asc"
            with ssh_client.open_sftp() as sftp:
                with sftp.file(temp_key_file, "w") as remote_file:
                    remote_file.write(public_key)

            # Importar la clave en el dispositivo
            stdin, stdout, stderr = ssh_client.exec_command(f"sudo gpg --import {temp_key_file}")
            error = stderr.read().decode().strip()
            
            # Eliminar el archivo temporal
            ssh_client.exec_command(f"rm {temp_key_file}")
            ssh_client.close()

            if error and "imported" not in error and "not changed" not in error:
                return JsonResponse({"error": f"Error importing key: {error}"}, status=400)
                
            return JsonResponse({
                "message": "Key imported successfully",
            })
            
        except Exception as e:
            return JsonResponse({"error": f"Failed to import key: {str(e)}"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@login_required
def delete_user(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)
        user.delete()
    return redirect("monitorize:users")

@login_required
def edit_user(request,user_id):
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return JsonResponse({"message": "User updated successfully."})
        else:
            return JsonResponse({"errors": form.errors}, status=400)
    return redirect("monitorize:users")

@login_required
def delete_device(request, device_id):
    if request.method == "POST":
        device = get_object_or_404(Device, id=device_id)
        device.delete()
    return redirect("monitorize:devices")

@login_required
def edit_device(request, device_id):
    if request.method == "POST":
        device = get_object_or_404(Device, id=device_id)
        form = DeviceChangeForm(request.POST, instance=device)
        if form.is_valid():
            form.save()
            return JsonResponse({"message": "Device updated successfully."})
        else:
            return JsonResponse({"errors": form.errors}, status=400)
    return redirect("monitorize:devices")

@login_required
def delete_file(request, file_id):
    if request.method == "POST":
        file_instance = get_object_or_404(File, id=file_id)
        file_instance.delete()
    return redirect("monitorize:device_detail", hostname=file_instance.device.hostname)
