from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator, FileExtensionValidator, validate_image_file_extension
from django.core.exceptions import ValidationError

import uuid
from PIL import Image
import os
from django.conf import settings

def get_unique_filepath(instance, filename):
    extension = filename.split('.')[-1]
    unique_filename = f'{uuid.uuid4()}.{extension}'
    upload_path = f'uploads/company/{unique_filename}'
    
    # Create the full path
    full_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'company')
    
    # Create directories if they don't exist
    os.makedirs(full_path, exist_ok=True)
    
    return upload_path

def validate_image_size(value):
    limit = 5 << 20  # 5 MB in bytes (5 * 1024 * 1024)
    if value.size > limit:
         raise ValidationError(f"Image size should not exceed 5 MB. Current size: {value.size / 1024 / 1024:.2f} MB")
     
def validate_image_format(value):
    try:
        img = Image.open(value)
        img.verify()
    except (IOError, SyntaxError):
        raise ValidationError("Invalid image file.")   

class User(AbstractUser):
    is_customer = models.BooleanField(default=False)
    is_company = models.BooleanField(default=False)
    email = models.EmailField(max_length=100, unique=True)

class Company(models.Model):
    FIELD_CHOICES = (
        ('All in One', 'All in One'),
        ('Air Conditioner', 'Air Conditioner'),
        ('Carpentry', 'Carpentry'),
        ('Electricity', 'Electricity'),
        ('Gardening', 'Gardening'),
        ('Home Machines', 'Home Machines'),
        ('House Keeping', 'House Keeping'),
        ('Interior Design', 'Interior Design'),
        ('Locks', 'Locks'),
        ('Painting', 'Painting'),
        ('Plumbing', 'Plumbing'),
        ('Water Heaters', 'Water Heaters'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    field = models.CharField(max_length=100, choices=FIELD_CHOICES)
    description = models.TextField(max_length=500, blank=True)
    rating = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(0)], default=0)
    image = models.ImageField(
        upload_to=get_unique_filepath,
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg']),
            validate_image_size,
            validate_image_format
        ]
    )

    def __str__(self):
        return self.user.username

    def can_create_service(self, service_field):
        return self.field == 'All in One' or self.field == service_field

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    date_of_birth = models.DateField()

    def __str__(self):
        return self.user.username
