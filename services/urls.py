from django.urls import path
from . import views 

app_name = 'services'

urlpatterns = [
    path('create/', views.create, name='services_create'),
    path('<int:id>', views.index, name='index'),
    path('<int:id>/request_service/', views.request_service, name='request_service'),
    path('<slug:field>/', views.service_field, name='services_field'),

    path('', views.service_list, name='service_list'),
    path('most-requested/', views.most_requested_services, name='most_requested'),
    path('category/<str:category>/', views.services_by_category, name='services_by_category'),
    
    # Individual service
    path('service/<int:service_id>/', views.service_detail, name='service_detail'),
    path('service/<int:service_id>/request/', views.request_service, name='request_service'),
    
    # Service management (for companies)
    path('create/', views.create_service, name='create_service'),
    # path('service/<int:service_id>/edit/', views.edit_service, name='edit_service'),
    # path('service/<int:service_id>/delete/', views.delete_service, name='delete_service'),
    
    # Service requests management
    path('requests/', views.ServiceRequest, name='service_requests'),
    path('request/<int:request_id>/', views.request_service, name='request_detail'),
    # path('request/<int:request_id>/rate/', views.rate_service, name='rate_service'),
]

