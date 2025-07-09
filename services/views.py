from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from users.models import Company, Customer, User
from utils import calculate_age  

from .models import Service, ServiceRequest, Review
from .forms import CreateNewService, RequestServiceForm, ReviewForm


def service_list(request):
    services = Service.objects.all().order_by("-date")
    print(f"Number of services found: {services.count()}")  # DEBUG line
    return render(request, 'services/list.html', {'services': services})


def index(request, id):
    service = Service.objects.get(id=id)
    return render(request, 'services/single_service.html', {'service': service})


def create(request):
    if not request.user.is_company:
        return redirect('services_list')
        
    if request.method == 'POST':
        form = CreateNewService(request.POST, company=request.user.company)
        if form.is_valid():
            field = form.cleaned_data['field']
            company = request.user.company
            
            service = Service(
                company=company,
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                price_hour=form.cleaned_data['price_hour'],
                field=field
            )
            service.save()
            return redirect('services_list')
    else:
        form = CreateNewService(company=request.user.company)
    return render(request, 'services/create.html', {'form': form})


def service_field(request, field):
    # Convert URL-friendly format to the actual field name
    field = field.replace('-', ' ').title()
    services = Service.objects.filter(field=field)
    
    return render(request, 'services/field.html', {'services': services, 'field': field})


def request_service(request, id):
    if not request.user.is_customer:
        return redirect('services_list')
        
    service = Service.objects.get(id=id)
    if request.method == 'POST':
        form = RequestServiceForm(request.POST)
        if form.is_valid():
            service_request = ServiceRequest(
                service=service,
                customer=request.user.customer,
                requested_date=form.cleaned_data['requested_date'],
                address=form.cleaned_data['address'],
                hours_needed=form.cleaned_data['hours_needed'],
                notes=form.cleaned_data['notes']
            )
            service_request.save()
            # Redirect to the user's profile instead of the requests list
            return redirect('profile', username=request.user.username)
    else:
        form = RequestServiceForm()
    return render(request, 'services/request_service.html', {'form': form, 'service': service})

@login_required
def service_requests_list(request):
    if request.user.is_customer:
        # For customers, show their own requests
        requests = ServiceRequest.objects.filter(
            customer=request.user.customer
        ).select_related('service', 'service__company', 'customer', 'customer__user'
        ).order_by('-created_at')  # Added ordering here
    else:
        # For companies, show requests for their services
        requests = ServiceRequest.objects.filter(
            service__company=request.user.company
        ).select_related('service', 'service__company', 'customer', 'customer__user'
        ).order_by('-created_at')  # Added ordering here
    
    return render(request, 'services/requests_list.html', {'requests': requests})

@login_required
def service_request_detail(request, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    # Check if user has permission to view this request
    if not (request.user.is_customer and service_request.customer == request.user.customer) and \
       not (request.user.is_company and service_request.service.company == request.user.company):
        return redirect('services_list')
    
    # Get review if it exists
    try:
        review = Review.objects.get(service_request=service_request)
    except Review.DoesNotExist:
        review = None
    
    # Check if user can review
    can_review = (
        request.user.is_customer and 
        service_request.customer == request.user.customer and 
        service_request.status == 'COMPLETED' and 
        review is None
    )
    
    context = {
        'request': service_request,
        'review': review,
        'can_review': can_review
    }
    
    return render(request, 'services/request_detail.html', context)

@login_required
def update_service_request(request, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    # Only company can update status
    if not request.user.is_company or service_request.service.company != request.user.company:
        return redirect('services_list')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(ServiceRequest._meta.get_field('status').choices):
            service_request.status = new_status
            service_request.save()
    return redirect('service_request_detail', request_id=request_id)

@login_required
def cancel_service_request(request, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    # Only customer who created the request can cancel it
    if not request.user.is_customer or service_request.customer != request.user.customer:
        return redirect('services_list')
    
    if request.method == 'POST':
        service_request.status = 'CANCELLED'
        service_request.save()
    return redirect('service_requests_list')

@login_required
def create_review(request, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    
    # Verify that the customer can review this service
    if not (request.user.is_customer and 
            service_request.customer == request.user.customer and 
            service_request.status == 'COMPLETED' and 
            not Review.objects.filter(service_request=service_request).exists()):
        return redirect('service_requests_list')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.service_request = service_request
            review.customer = request.user.customer
            review.service = service_request.service
            review.save()
            return redirect('service_request_detail', request_id=request_id)
    else:
        form = ReviewForm()
    
    return render(request, 'services/create_review.html', {
        'form': form,
        'service_request': service_request
    })
