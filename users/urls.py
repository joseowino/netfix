from django.urls import path
from django.contrib.auth import views as auth_views

from .forms import UserLoginForm
from . import views as v

app_name = 'users'

urlpatterns = [
    path('', v.register, name='register'),
    path('profile/', v.profile, name='profile'),
    path('company/', v.CompanySignUpView.as_view(), name='register_company'),
    path('customer/', v.CustomerSignUpView.as_view(), name='register_customer'),
    path('login/', v.LoginUserView, name='login_user'),
    path('profile/company/<str:username>/', v.company_profile, name='company_profile'),
    path('profile/customer/<str:username>/', v.customer_profile, name='customer_profile'),
    path('profile/update-image/', v.update_profile_image, name='update_profile_image'),  # Add this line
    path('profile/update-company/', v.update_profile_image, name='company_profile_update'),

]