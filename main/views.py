from django.shortcuts import render, get_object_or_404
from django.contrib.auth import logout as django_logout
from users.models import User, Company, Customer
from services.models import Service, ServiceRequest


def home(request):
    return render(request, "main/home.html", {})



def customer_profile(request, name):
    """Display customer profile with their service requests."""
    user = get_object_or_404(User, username=name)

    # Ensure the user is actually a customer
    if not user.is_customer:
        return render(request, 'main/error.html', {
            'error_message': 'This user is not a customer.'
        })

    try:
        customer = Customer.objects.get(user=user)
        # Get customer's service requests
        service_requests = ServiceRequest.objects.filter(customer=customer).order_by('-request_date')
    except Customer.DoesNotExist:
        customer = None
        service_requests = []

    context = {
        'user': user,
        'customer': customer,
        'service_requests': service_requests,
        'is_customer_profile': True
    }

    return render(request, 'users/customer_profile.html', context)


def company_profile(request, name):
    # fetches the company user and all of the services available by it
    user = User.objects.get(username=name)
    services = Service.objects.filter(
        company=Company.objects.get(user=user)).order_by("-date")

    return render(request, 'users/profile.html', {'user': user, 'services': services})


def logout(request):
    django_logout(request)
    return render(request, "main/logout.html")
