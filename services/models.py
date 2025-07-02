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
    