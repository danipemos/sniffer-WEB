from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DeviceCreationForm, PrivateKeyCreationForm
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
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "home.html", {"user_form": form})

@login_required
def add_private_key(request):
    if request.method == "POST":
        form = PrivateKeyCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = PrivateKeyCreationForm()
    return render(request, "home.html", {"private_key_form": form})

@login_required
def add_device(request):
    if request.method == "POST":
        form = DeviceCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = DeviceCreationForm()
    return render(request, "home.html", {"device_form": form})
