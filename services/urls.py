from django.urls import path
from . import views as v

app_name = 'services'

urlpatterns = [
    path('', v.service_list, name='service_list'),
    path('most_requested/', v.most_requested_services, name='most_requested_services'),
    path('create/', v.create, name='service_create'),
    path('<int:id>/', v.service_detail, name='service_detail'),
    path('<int:id>/request_service/', v.request_service, name='request_service'),
    path('<slug:field>/', v.service_field, name='service_field'), #updated
    path('rate/<int:service_id>/', v.rate_service, name='rate_service'),
    # path('services/for-dropdown/', v.get_services_for_dropdown, name='get_services_for_dropdown'),
]