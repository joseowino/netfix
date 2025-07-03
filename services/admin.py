# services/admin.py
from django.contrib import admin
from .models import Service, ServiceRequest

admin.site.register(Service)
admin.site.register(ServiceRequest)