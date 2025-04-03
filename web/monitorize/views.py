from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import DeviceCreationForm, PrivateKeyCreationForm
from .models import Device
from users.forms import UserCreationForm

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

def ssh_terminal_view(request, device_id):
    device = get_object_or_404(Device, id=device_id)
    return render(request, "ssh_terminal.html", {"device": device})
