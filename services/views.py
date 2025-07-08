from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from users.models import Company, Customer, User
from django.contrib.auth.decorators import login_required

from .models import Service, ServiceRequest
from .forms import ServiceForm, ServiceRequestForm, ServiceSearchForm

def service_list(request):
    services = Service.objects.all().order_by("-date")
    return render(request, 'services/list.html', {'services': services})


def index(request, id):
    service = Service.objects.get(id=id)
    return render(request, 'services/single_service.html', {'service': service})


def create(request):
    return render(request, 'services/create.html',
            {'form': ServiceForm(company=request.user.company)})
    

def service_field(request, field):
    # search for the service present in the url
    field = field.replace('-', ' ').title()
    services = Service.objects.filter(
        field=field)
    return render(request, 'services/field.html', {'services': services, 'field': field})


def request_service(request, id):
    return render(request, 'services/request_service.html', {})

def create_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST, company=request.user.company)
        if form.is_valid():
            service = form.save(commit=False)
            service.company = request.user.company
            service.save()
    else:
        form = ServiceForm(company=request.user.company)

    return render(request, 'services/create.html', {'form': form})


def service_list(request):
    """
    Display all services ordered by newest first with search and filter functionality
    """
    # Get all services ordered by newest first
    services = Service.objects.all().order_by('-date')
    
    # Handle search and filtering
    search_form = ServiceSearchForm(request.GET)
    
    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        field = search_form.cleaned_data.get('field')
        min_price = search_form.cleaned_data.get('min_price')
        max_price = search_form.cleaned_data.get('max_price')
        sort_by = search_form.cleaned_data.get('sort_by')
        
        # Apply filters
        if query:
            services = services.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query) |
                Q(company__username__icontains=query)
            )
        
        if field:
            services = services.filter(field=field)
        
        if min_price:
            services = services.filter(price_hour__gte=min_price)
        
        if max_price:
            services = services.filter(price_hour__lte=max_price)
        
        # Apply sorting
        if sort_by:
            services = services.order_by(sort_by)
    
    # Pagination - 12 services per page
    paginator = Paginator(services, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'services': page_obj,
        'search_form': search_form,
        'total_services': services.count(),
    }
    
    return render(request, 'services/list.html', context)


def service_detail(request, service_id):
    """
    Display individual service details
    """
    service = get_object_or_404(Service, id=service_id)
    
    # Check if current user can request this service
    can_request = False
    if request.user.is_authenticated:
        # Only customers can request services, not companies
        if hasattr(request.user, 'customer'):
            can_request = True
    
    context = {
        'service': service,
        'can_request': can_request,
    }
    
    return render(request, 'services/service_detail.html', context)


@login_required
def request_service(request, service_id):
    """
    Allow customers to request a service
    """
    service = get_object_or_404(Service, id=service_id)
    
    # Check if user is a customer
    if not hasattr(request.user, 'customer'):
        messages.error(request, "Only customers can request services.")
        return redirect('services:service_detail', service_id=service_id)
    
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.customer = request.user.customer
            service_request.service = service
            service_request.save()
            
            messages.success(request, f"Service '{service.name}' requested successfully!")
            return redirect('users:profile')
    else:
        form = ServiceRequestForm()
    
    context = {
        'form': form,
        'service': service,
    }
    
    return render(request, 'services/request_service.html', context)


def services_by_category(request, category):
    """
    Display services filtered by category
    """
    # Validate category
    valid_categories = [choice[0] for choice in Service.FIELD_CHOICES]
    if category not in valid_categories:
        messages.error(request, "Invalid category.")
        return redirect('services:service_list')
    
    services = Service.objects.filter(field=category).order_by('-date')
    
    # Pagination
    paginator = Paginator(services, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'services': page_obj,
        'category': category,
        'total_services': services.count(),
    }
    
    return render(request, 'services/category_services.html', context)


def most_requested_services(request):
    """
    Display most requested services
    """
    from django.db.models import Count
    
    # Get services with request count, ordered by most requested
    services = Service.objects.annotate(
        request_count=Count('service_requests')
    ).filter(request_count__gt=0).order_by('-request_count')
    
    # Pagination
    paginator = Paginator(services, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'services': page_obj,
        'total_services': services.count(),
    }
    
    return render(request, 'services/most_requested.html', context)