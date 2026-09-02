from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render


def landing(request):
    """Landing page view."""
    return render(request, "monitor/landing.html")


def signup(request):
    """User signup view."""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("dashboard")
    else:
        form = UserCreationForm()
    return render(request, "monitor/signup.html", {"form": form})
