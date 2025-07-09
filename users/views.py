from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.views.generic import CreateView

from .forms import CustomerSignUpForm, CompanySignUpForm, UserLoginForm
from .models import User, Company, Customer
from services.models import ServiceRequest, Service
from utils import calculate_age


def register(request):
    return render(request, 'users/register.html')


class CustomerSignUpView(CreateView):
    model = User
    form_class = CustomerSignUpForm
    template_name = 'users/register_customer.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'customer'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        # Specify the backend when logging in
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('/')


class CompanySignUpView(CreateView):
    model = User
    form_class = CompanySignUpForm
    template_name = 'users/register_company.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'company'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        # Specify the backend when logging in
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('/')
        

def LoginUserView(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                if user.is_customer:
                    return redirect('profile', username=user.username)
                else:
                    return redirect('profile', username=user.username)
            else:
                form.add_error(None, "Invalid email or password.")
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})

def ProfileView(request, username):
    user = get_object_or_404(User, username=username)
    
    if user.is_customer:
        customer = Customer.objects.get(user=user)
        user_age = calculate_age(customer.date_of_birth)
        
        # Get all service requests for this customer, ordered by most recent first
        service_history = ServiceRequest.objects.filter(
            customer=customer
        ).select_related('service', 'service__company').order_by('-requested_date')
        
        return render(request, 'users/profile.html', {
            'user': user,
            'user_age': user_age,
            'sh': service_history
        })
    
    elif user.is_company:
        company = Company.objects.get(user=user)
        services = Service.objects.filter(company=company)
        
        # Get all service requests for this company's services
        service_requests = ServiceRequest.objects.filter(
            service__company=company
        ).select_related('service', 'customer', 'customer__user').order_by('-requested_date')
        
        return render(request, 'users/profile.html', {
            'user': user,
            'services': services,
            'service_requests': service_requests
        })
    
    return redirect('/')
