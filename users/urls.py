from django.urls import path
from . import views as v

urlpatterns = [
    path('', v.register, name='register'),
    path('company/', v.CompanySignUpView.as_view(), name='register_company'),
    path('customer/', v.CustomerSignUpView.as_view(), name='register_customer'),
]
