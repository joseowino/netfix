from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from users.models import User, Company, Customer
from services.models import Service

def home(request):
    return render(request, 'main/home.html', {'user': request.user})

@login_required
def customer_profile(request, name):
    user = get_object_or_404(User, username=name)
    profile = get_object_or_404(Customer, user=user)
    requested_services = ServiceRequest.objects.filter(customer=profile)
    return render(request, 'users/customer_profile.html', {
        'user': user,
        'profile': profile,
        'requested_services': requested_services
    })

@login_required
def company_profile(request, name):
    user = get_object_or_404(User, username=name)
    profile = get_object_or_404(Company, user=user)
    services = Service.objects.filter(company=profile).order_by("-date_created")
    return render(request, 'users/company_profile.html', {
        'user': user,
        'profile': profile,
        'services': services
    })