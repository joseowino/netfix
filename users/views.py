from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views.generic import CreateView

from .forms import CustomerSignUpForm, CompanySignUpForm, UserLoginForm
from .models import User


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
        login(self.request, user)
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
        login(self.request, user)
        return redirect('/')


def LoginUserView(request):
    """Handle user login using email/username and password with profile redirection."""
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user_obj = form.cleaned_data['user_obj']
            password = form.cleaned_data['password']

            # Authenticate the user
            user = authenticate(request, username=user_obj.username, password=password)
            if user is not None:
                login(request, user)

                # Redirect to appropriate profile page based on user type
                if user.is_company:
                    return redirect('company_profile', name=user.username)
                elif user.is_customer:
                    return redirect('customer_profile', name=user.username)
                else:
                    # Fallback to home page for users without specific type
                    return redirect('/')
            else:
                form.add_error(None, 'Invalid email/username or password.')
    else:
        form = UserLoginForm()

    return render(request, 'users/login.html', {'form': form})
