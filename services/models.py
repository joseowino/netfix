from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from users.models import Company, Customer, User


class Service(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    description = models.TextField()
    price_hour = models.DecimalField(decimal_places=2, max_digits=100)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=1,
        help_text="Rating from 1 to 5 stars"
    )
    
    field = models.CharField(max_length=30, blank=False,
                             null=False, choices=Company.FIELD_CHOICES)
    date = models.DateTimeField(auto_now=True, null=False)

    def __str__(self):
        return self.name

    def get_request_count(self):
        return self.servicerequest_set.count()

    @staticmethod
    def get_most_requested(limit=6):
        from django.db.models import Count
        return Service.objects.annotate(
            request_count=Count('servicerequest')
        ).order_by('-request_count')[:limit]


class ServiceRequest(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    requested_date = models.DateTimeField()
    address = models.CharField(max_length=255, null=True, blank=True)  # Make it nullable initially
    hours_needed = models.PositiveIntegerField(null=True, blank=True)  # Make it nullable initially
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Make it nullable initially
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled')
    ], default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calculate total cost before saving
        if self.hours_needed and self.service and not self.total_cost:
            self.total_cost = self.service.price_hour * self.hours_needed
        super().save(*args, **kwargs)

class Review(models.Model):
    service_request = models.OneToOneField('ServiceRequest', on_delete=models.CASCADE)
    customer = models.ForeignKey('users.Customer', on_delete=models.CASCADE)
    service = models.ForeignKey('Service', on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.customer.user.username} for {self.service.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update service average rating
        service_reviews = Review.objects.filter(service=self.service)
        avg_rating = service_reviews.aggregate(models.Avg('rating'))['rating__avg']
        self.service.rating = round(avg_rating) if avg_rating else 0
        self.service.save()
        
        # Update company average rating
        company_reviews = Review.objects.filter(service__company=self.service.company)
        avg_company_rating = company_reviews.aggregate(models.Avg('rating'))['rating__avg']
        self.service.company.rating = round(avg_company_rating) if avg_company_rating else 0
        self.service.company.save()
