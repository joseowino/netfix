from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path('login/', views.LoginUserView, name='login'),
    path('register/', views.register, name='register'),
    path('register/company/', views.CompanySignUpView.as_view(), name='register_company'),
    path('register/customer/', views.CustomerSignUpView.as_view(), name='register_customer'),
]
