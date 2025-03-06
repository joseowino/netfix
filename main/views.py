from django.shortcuts import render, redirect
from django.contrib.auth import logout as django_logout
from services.models import Service
from django.db.models import Count

def home(request):
    # Extract all predefined fields from the Service model's choices
    fields = [choice[0] for choice in Service.FIELD_CHOICES]

    # Get the selected category from the GET request
    selected_field = request.GET.get('field', None)

    # Filter services based on the selected category
    services = (
        Service.objects.filter(field=selected_field).order_by('-date_created')
        if selected_field
        else Service.objects.all()  # Default to all services if no field is selected
    )

    # Get the most requested services
    most_requested_services = Service.objects.annotate(request_count=Count('servicerequest')).filter(request_count__gt=0).order_by('-request_count')[:10]

    return render(request, 'main/home.html', {
        'fields': fields,
        'services': services,
        'selected_field': selected_field,
        'most_requested_services': most_requested_services,  # Pass most requested services to the template
    })

def logout(request):
    django_logout(request)
    return redirect("main:home")
