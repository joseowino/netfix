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
    """Display company profile with their services and information."""
    user = get_object_or_404(User, username=name)

    # Ensure the user is actually a company
    if not user.is_company:
        return render(request, 'main/error.html', {
            'error_message': 'This user is not a company.'
        })

    try:
        company = Company.objects.get(user=user)
        # Get company's services ordered by creation date (newest first)
        services = Service.objects.filter(company=company).order_by('-date')

        # Calculate some statistics
        total_services = services.count()
        total_requests = sum(service.total_requests for service in services)
        average_rating = 0
        if services.exists():
            ratings = [service.average_rating for service in services if service.average_rating > 0]
            if ratings:
                average_rating = sum(ratings) / len(ratings)

    except Company.DoesNotExist:
        company = None
        services = []
        total_services = 0
        total_requests = 0
        average_rating = 0

    context = {
        'user': user,
        'company': company,
        'services': services,
        'total_services': total_services,
        'total_requests': total_requests,
        'average_rating': average_rating,
        'is_company_profile': True
    }

    return render(request, 'users/company_profile.html', context)


def logout(request):
    django_logout(request)
    return render(request, "main/logout.html")
