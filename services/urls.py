from django.urls import path
from . import views as v

urlpatterns = [  
    path('', v.service_list, name='services_list'),
    path('<int:id>/', v.index, name='service_detail'),
    path('create/', v.create, name='create_service'),
    path('<str:field>/', v.service_field, name='service_field'),
    path('<int:id>/request_service/', v.request_service, name='request_service'),
    # Service request management
    path('requests/', v.service_requests_list, name='service_requests_list'),
    path('requests/<int:request_id>/', v.service_request_detail, name='service_request_detail'),
    path('requests/<int:request_id>/update/', v.update_service_request, name='update_service_request'),
    path('requests/<int:request_id>/cancel/', v.cancel_service_request, name='cancel_service_request'),
    path('request/<int:request_id>/review/', v.create_review, name='create_review'),
]
