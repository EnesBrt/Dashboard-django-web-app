from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import CustomUserCreationForm
from .forms import LoginForm
from django.contrib.auth.views import LogoutView


def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = CustomUserCreationForm()
    return render(request, "signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            return redirect("dashboard")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    return LogoutView.as_view()(request)


def dashboard(request):
    return render(request, "dashboard.html")
