from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect

from users.models import Company, Customer, User

from .models import Service
from .forms import ServiceForm


def service_list(request):
    services = Service.objects.all().order_by("-date")
    return render(request, 'services/list.html', {'services': services})


def index(request, id):
    service = Service.objects.get(id=id)
    return render(request, 'services/single_service.html', {'service': service})


def create(request):
    return render(request, 'services/create.html', {})


def service_field(request, field):
    # search for the service present in the url
    field = field.replace('-', ' ').title()
    services = Service.objects.filter(
        field=field)
    return render(request, 'services/field.html', {'services': services, 'field': field})


def request_service(request, id):
    return render(request, 'services/request_service.html', {})


# In your views.py
from .forms import ServiceForm, ServiceRequestForm

def create_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST, company=request.user.company)
        if form.is_valid():
            service = form.save(commit=False)
            service.company = request.user.company
            service.save()
    else:
        form = ServiceForm(company=request.user.company)