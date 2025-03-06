from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Count
from .models import Service, ServiceRequest,update_service_rating,ServiceRating
from .forms import CreateNewService, RequestServiceForm,ServiceRatingForm
from users.models import Company, Customer, User
from django.http import JsonResponse
# from django.db.models import Avg


def get_services_for_dropdown(request):
    # Fetch all services (or you can filter as needed)
    services = Service.objects.all().order_by('-date_created')

    # Prepare the response as a list of dictionaries
    service_list = []
    for service in services:
        service_list.append({
            'id': service.id,
            'name': service.name,
            'description': service.description,
            'field': service.field,
        })

    return JsonResponse({'services': service_list})

def service_list(request):
   # Query all services and order them by creation date (most recent first)
    services = Service.objects.all().order_by('-date_created')
    
    print(f"Number of services: {services.count()}")

    # Fetch unique fields for filtering options in the template (optional)
    fields = Service.objects.values_list('field', flat=True).distinct()

    return render(request, 'services/service_list.html', {
        'services': services,
        'fields': fields,
    })

def most_requested_services(request):
    services = Service.objects.annotate(request_count=Count('servicerequest')).filter(request_count__gt=0).order_by('-request_count')[:10]
    return render(request, 'services/most_requested_services.html', {'services': services})

@login_required
def create(request):
    #Check if the user is a company
    if request.user.is_customer:
        #Prevent customers from accessing the services cfreation page
        messages.error(request, 'You must be a company to create a service.')
        return redirect('users:customer_profile', username=request.user.username)
    if request.method == 'POST':
        form = CreateNewService(request.POST,user=request.user)
        if form.is_valid():
            service = form.save(commit=False)
            #Check if the service's field matches the company's field
            if request.user.company.field != 'All in One' and service.field != request.user.company.field:
                messages.error(request, 'You can only create services in your field of work.')
                return redirect('services:service_create')
            #Assign the company to the service and save
            service.company = request.user.company
            service.save()
            messages.success(request, 'Service created successfully.')
            return redirect('services:service_list')
    else:
        form = CreateNewService(user=request.user)
    return render(request, 'services/service_create.html', {'form': form})



def service_detail(request, id):
    service = get_object_or_404(Service, id=id)
    company = service.company  # Get the company that created the service

    # Check if the user has already rated this service
    user_rating = None
    if request.user.is_authenticated:
        user_rating = ServiceRating.objects.filter(service=service, user=request.user).first()

    if request.method == 'POST' and user_rating is None:
        # Handle rating submission
        form = ServiceRatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.service = service
            rating.user = request.user
            rating.save()

            # Update the service's average rating
            update_service_rating(service)

            return redirect('services:service_detail', id=service.id)
    else:
        form = ServiceRatingForm()

    return render(request, 'services/service_detail.html', {
        'service': service,
        'company': company,
        'form': form,
        'user_rating': user_rating
    })
    
@login_required
def rate_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    if request.method == "POST":
        rating = int(request.POST.get("rating", 0))
        review = request.POST.get("review", "")

        # Ensure the rating is within valid bounds
        if 0 <= rating <= 5:
            # Create or update the rating for the current user
            ServiceRating.objects.update_or_create(
                service=service, user=request.user,
                defaults={"rating": rating, "review": review}
            )
            # Update the average service rating
            update_service_rating(service)
            return redirect("services:service_detail", id=service.id)

        return HttpResponse("Invalid rating", status=400)

    return HttpResponse("Invalid request method", status=405)
@login_required
def request_service(request, id):
    service = get_object_or_404(Service, id=id)
    if request.method == 'POST':
        form = RequestServiceForm(request.POST)
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.customer = request.user.customer
            service_request.service = service
            service_request.save()
            messages.success(request, 'Service requested successfully.')
            return redirect('services:service_list')
    else:
        form = RequestServiceForm()
    return render(request, 'services/request_service_form.html', {'form': form, 'service': service})

def service_field(request, field):
    services = Service.objects.filter(field=field).order_by('-date_created')
    return render(request, 'services/service_field.html', {'services': services, 'field': field})

@login_required
def company_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Company, user=user) #Get the company profile
    services = Service.objects.filter(company=profile)#Get services created by the company
    return render(request, 'users/company_profile.html', {
        'user': user,
        'profile': profile,
        'services': services
    })

@login_required
def customer_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Customer, user=user)
    available_services = Service.objects.all()
    requested_services = ServiceRequest.objects.filter(customer=profile)
    return render(request, 'users/customer_profile.html', {
        'user': user,
        'profile': profile,
        'available_services': available_services,
        'requested_services': requested_services
    })