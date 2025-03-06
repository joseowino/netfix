from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import CustomerSignUpForm, CompanySignUpForm, UserLoginForm, ProfileImageForm
from .models import User, Company, Customer
from services.models import Service, ServiceRequest

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
        user = form.save(commit=False)
        user.is_customer = True
        user.save()
        
         # Pass the 'birth' value from the form to the Customer model
        birth = form.cleaned_data.get('birth')
        Customer.objects.create(user=user, birth=birth)
        # Customer.objects.create(user=user)
        messages.success(self.request, 'Registration successful. Please log in.')
        return redirect('users:login_user')

class CompanySignUpView(CreateView):
    model = User
    form_class = CompanySignUpForm
    template_name = 'users/register_company.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'company'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_company = True
        user.save()
        Company.objects.create(user=user, field=form.cleaned_data['field'])
        messages.success(self.request, 'Registration successful. Please log in.')
        return redirect('users:login_user')

def LoginUserView(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user:
                print(f"Authenticated user: {user.username}, is_company: {user.is_company}, is_customer: {user.is_customer}")
                login(request, user)
                if user.is_company:
                    print(f"Redirecting to company profile for {user.username}")
                    return redirect('users:company_profile', username=user.username)
                elif user.is_customer:
                    print(f"Redirecting to customer profile for {user.username}")
                    return redirect('users:customer_profile', username=user.username)
                else:
                    messages.error(request, 'User type is not defined.')
            else:
                print("Authentication failed.")
                messages.error(request, 'Invalid email or password.')
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})

def company_profile(request, username):
    user = get_object_or_404(User, username=username)

    #Retrieve the logged-in user's company
    profile = get_object_or_404(Company, user=user)
    services = Service.objects.filter(company=profile)
    
     # Check if the user is the company owner
    is_company_owner = request.user == user  # Compare the logged-in user with the company owner

    return render(request, 'users/company_profile.html', {
        'user': user,
        'profile': profile,
        'services': services,
        'is_company_owner': is_company_owner,  # Pass the comparison result
    })
@login_required
def profile(request):
    if request.user.is_customer:
        profile = get_object_or_404(Customer, user=request.user)
    else:
        profile = get_object_or_404(Company, user=request.user)
    return render(request, 'users/profile.html', {'profile': profile})

@login_required
def customer_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Customer, user=user)
    print(profile.birth)
    requested_services = ServiceRequest.objects.filter(customer=profile)
    available_services = Service.objects.all()  # Get all services
    
    total_cost = 0
    for service_request in requested_services:  # Changed variable name from 'request' to 'service_request'
        service_cost = service_request.service_time * service_request.service.price_hour
        total_cost += service_cost
        service_request.service_cost = service_cost

    return render(request, 'users/customer_profile.html', {
        'user': user,
        'profile': profile,
        'requested_services': requested_services,
        'available_services': available_services,
        'total_cost': total_cost,  # Pass total cost to the template
    })

@login_required
def update_profile_image(request):
    if request.user.is_customer:
        profile = request.user.customer  # customer model has a OneToOne relationship with User
    elif request.user.is_company:
        profile = request.user.company  # Assuming your Company model has a OneToOne relationship with the User model
    else:
        # If the user is not a customer, you can return an error or redirect as appropriate
        messages.error(request, 'Only customers can update their profile image.')
        return redirect('users:profile')  # You can redirect to a different page

    if request.method == 'POST':
        form = ProfileImageForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile image updated successfully.')
                # Redirect to the appropriate profile page
            if request.user.is_company:
                return redirect('users:company_profile', username=request.user.username)
            else:
                return redirect('users:customer_profile', username=request.user.username)
    else:
        form = ProfileImageForm(instance=profile)

    return render(request, 'users/update_profile_image.html', {'form': form})
