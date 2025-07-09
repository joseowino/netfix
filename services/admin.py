from django.contrib import admin

from .models import Service, ServiceRequest, Review


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price_hour", "field", "date")

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "service", "customer", "requested_date", "status", "created_at")

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "service", "customer", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("service__name", "customer__user__username", "comment")
