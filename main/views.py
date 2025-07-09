from django.shortcuts import render
from django.contrib.auth import logout as django_logout
from django.contrib import messages
from services.models import Service

def home(request):
    popular_services = Service.get_most_requested()
    return render(request, "main/home.html", {
        'popular_services': popular_services
    })

def logout(request):
    django_logout(request)
    messages.success(request, "You have been logged out successfully.")
    return render(request, "main/logout.html")