from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import login,logout
from .forms import LoginForm
# Create your views here.

def login_user(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.user)
            return redirect("admin:index")
    else:
        if request.user.is_authenticated:
            return redirect("admin:index")
        form = LoginForm()
    return render(request, "login.html", {"form": form})

def logout_user(request):
    logout(request)
    return redirect("users:login")