from django.urls import path
from . import views as v

app_name = "main"

urlpatterns = [
    path('', v.home, name='home'),
    path('logout/', v.logout, name='logout'),
#    path('services/', v.services_by_category, name='services_by_category'),  # Handle empty field case
    # path('services/<str:field>/', v.services_by_category, name='services_by_category_field'),  # Handle specific field case

]
