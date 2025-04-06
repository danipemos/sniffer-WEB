from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import DeviceCreationForm, PrivateKeyCreationForm
from .models import Device
from users.forms import UserCreationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import paramiko

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

    return render(request, "device_detail.html", {
        "device": device,
        "missing_credentials": missing_credentials,
    })
