from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from users.models import Company, Customer

class Service(models.Model):
    """
    Service model representing services offered by companies
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    description = models.TextField()
    price_hour = models.DecimalField(decimal_places=2, max_digits=10)
    rating = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)], 
        default=0
    )
    
    # Service field choices (cannot be 'All in One' as per requirements)
    FIELD_CHOICES = (
        ('Air Conditioner', 'Air Conditioner'),
        ('Carpentry', 'Carpentry'),
        ('Electricity', 'Electricity'),
        ('Gardening', 'Gardening'),
        ('Home Machines', 'Home Machines'),
        ('Housekeeping', 'Housekeeping'),  # Fixed spelling
        ('Interior Design', 'Interior Design'),
        ('Locks', 'Locks'),
        ('Painting', 'Painting'),
        ('Plumbing', 'Plumbing'),
        ('Water Heaters', 'Water Heaters'),
    )
    
    field = models.CharField(max_length=30, blank=False, null=False, choices=FIELD_CHOICES)
    
    # Auto-set creation date (use auto_now_add for creation time)
    date = models.DateTimeField(auto_now_add=True, null=False)
    
    # Track when service was last updated
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']  # Order by newest first
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
    
    def __str__(self):
        return f"{self.name} - {self.company.username}"
    
    def get_absolute_url(self):
        """Return URL for service detail page"""
        from django.urls import reverse
        return reverse('services:service_detail', args=[str(self.id)])
    
    @property
    def average_rating(self):
        """Calculate average rating from service requests"""
        requests = self.service_requests.filter(rating__isnull=False)
        if requests.exists():
            return requests.aggregate(models.Avg('rating'))['rating__avg']
        return 0
    
    @property
    def total_requests(self):
        """Get total number of requests for this service"""
        return self.service_requests.count()

class ServiceRequest(models.Model):
    """
    ServiceRequest model representing customer requests for services
    """
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name='service_requests'
    )
    service = models.ForeignKey(
        Service, 
        on_delete=models.CASCADE, 
        related_name='service_requests'
    )
    address = models.TextField(help_text="Address where service is required")
    service_time = models.PositiveIntegerField(
        help_text="Service time needed in hours",
        validators=[MinValueValidator(1), MaxValueValidator(24)]
    )
    
    # Calculated cost based on service price and time
    total_cost = models.DecimalField(
        decimal_places=2, 
        max_digits=10,
        null=True,
        blank=True
    )
    
    # Request status
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Date when service was requested
    request_date = models.DateTimeField(auto_now_add=True)
    
    # Optional rating from customer (1-5 stars)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Rate the service (1-5 stars)"
    )
    
    # Optional review from customer
    review = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-request_date']
        verbose_name = 'Service Request'
        verbose_name_plural = 'Service Requests'
    
    def __str__(self):
        return f"{self.customer.username} - {self.service.name}"
    
    def save(self, *args, **kwargs):
        """Calculate total cost before saving"""
        if self.service and self.service_time:
            self.total_cost = self.service.price_hour * self.service_time
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Return URL for service request detail"""
        from django.urls import reverse
        return reverse('services:request_detail', args=[str(self.id)])
    
    @property
    def company(self):
        """Get the company providing this service"""
        return self.service.company