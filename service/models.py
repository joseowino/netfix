from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from users.models import Company, Customer, User
from django.db.models import Avg


class Service(models.Model):
    FIELD_CHOICES = (
        ('Air Conditioner', 'Air Conditioner'),
        ('Carpentry', 'Carpentry'),
        ('Electricity', 'Electricity'),
        ('Gardening', 'Gardening'),
        ('Home Machines', 'Home Machines'),
        ('Housekeeping', 'Housekeeping'),
        ('Interior Design', 'Interior Design'),
        ('Locks', 'Locks'),
        ('Painting', 'Painting'),
        ('Plumbing', 'Plumbing'),
        ('Water Heaters', 'Water Heaters'),
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    description = models.TextField()
    price_hour = models.DecimalField(decimal_places=2, max_digits=5, validators=[MinValueValidator(0.00)])
    rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)
    field = models.CharField(max_length=30, choices=FIELD_CHOICES)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ServiceRequest(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    service_time = models.IntegerField(validators=[MinValueValidator(1)])
    date_requested = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.user.username} requested {self.service.name}"
    
class ServiceRating(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    review = models.TextField(blank=True, null=True)  # Optional field for the review

    def __str__(self):
        return f"{self.user.username} rated {self.service.name} - {self.rating}/5"
    
def update_service_rating(service):
    ratings = ServiceRating.objects.filter(service=service)
    if ratings.exists():
        average_rating = ratings.aggregate(Avg('rating'))['rating__avg']
        service.rating = round(average_rating)  # Round to the nearest whole number
        service.save()

