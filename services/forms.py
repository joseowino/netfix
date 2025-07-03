from django import forms
from django.core.exceptions import ValidationError
from .models import Service, ServiceRequest
from users.models import Company

class ServiceForm(forms.ModelForm):
    """
    Form for companies to create new services
    """
    
    class Meta:
        model = Service
        fields = ['name', 'description', 'field', 'price_hour']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter service name',
                'maxlength': '40'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your service in detail',
                'rows': 4
            }),
            'field': forms.Select(attrs={
                'class': 'form-control'
            }),
            'price_hour': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Price per hour',
                'min': '0.01',
                'step': '0.01'
            }),
        }
        labels = {
            'name': 'Service Name',
            'description': 'Service Description',
            'field': 'Service Category',
            'price_hour': 'Price per Hour ($)',
        }
        help_texts = {
            'name': 'Maximum 40 characters',
            'description': 'Provide detailed information about your service',
            'field': 'Select the category that matches your service',
            'price_hour': 'Enter the hourly rate for this service',
        }
    
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        # Filter field choices based on company's field of work
        if self.company:
            if self.company.field == 'All in One':
                # All in One companies can create services in any category
                # except 'All in One' (services cannot be 'All in One')
                pass  # Keep all choices as defined in model
            else:
                # Restrict to company's field of work only
                company_field = self.company.field
                filtered_choices = [(choice[0], choice[1]) for choice in Service.FIELD_CHOICES 
                                  if choice[0] == company_field]
                self.fields['field'].choices = filtered_choices
    
    def clean_price_hour(self):
        """Validate price is positive"""
        price = self.cleaned_data.get('price_hour')
        if price <= 0:
            raise ValidationError("Price must be greater than 0")
        return price
    
    def clean_name(self):
        """Validate service name is unique for this company"""
        name = self.cleaned_data.get('name')
        if self.company:
            # Check if company already has a service with this name
            existing_service = Service.objects.filter(
                company=self.company, 
                name__iexact=name
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing_service.exists():
                raise ValidationError("You already have a service with this name")
        return name
    
    def clean_field(self):
        """Validate field matches company's allowed fields"""
        field = self.cleaned_data.get('field')
        if self.company and self.company.field != 'All in One':
            if field != self.company.field:
                raise ValidationError(
                    f"Your company can only create {self.company.field} services"
                )
        return field


class ServiceRequestForm(forms.ModelForm):
    """
    Form for customers to request services
    """
    
    class Meta:
        model = ServiceRequest
        fields = ['address', 'service_time']
        widgets = {
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the complete address where service is needed',
                'rows': 3
            }),
            'service_time': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Hours needed',
                'min': '1',
                'max': '24'
            }),
        }
        labels = {
            'address': 'Service Address',
            'service_time': 'Service Duration (Hours)',
        }
        help_texts = {
            'address': 'Provide the complete address including any specific instructions',
            'service_time': 'Estimate how many hours the service will take (1-24 hours)',
        }
    
    def clean_service_time(self):
        """Validate service time is within reasonable limits"""
        service_time = self.cleaned_data.get('service_time')
        if service_time < 1:
            raise ValidationError("Service time must be at least 1 hour")
        if service_time > 24:
            raise ValidationError("Service time cannot exceed 24 hours")
        return service_time
    
    def clean_address(self):
        """Validate address is not empty"""
        address = self.cleaned_data.get('address')
        if not address or not address.strip():
            raise ValidationError("Please provide a valid address")
        return address.strip()


class ServiceSearchForm(forms.Form):
    """
    Form for searching and filtering services
    """
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search services...',
        }),
        label='Search'
    )
    
    # field = forms.ChoiceField(
    #     choices=[('', 'All Categories')] + Service.FIELD_CHOICES,
    #     required=False,
    #     widget=forms.Select(attrs={
    #         'class': 'form-control'
    #     }),
    #     label='Category'
    # )
    
    min_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min price',
            'min': '0',
            'step': '0.01'
        }),
        label='Min Price'
    )
    
    max_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max price',
            'min': '0',
            'step': '0.01'
        }),
        label='Max Price'
    )
    
    sort_by = forms.ChoiceField(
        choices=[
            ('date', 'Newest First'),
            ('-date', 'Oldest First'),
            ('price_hour', 'Price: Low to High'),
            ('-price_hour', 'Price: High to Low'),
            ('name', 'Name: A to Z'),
            ('-name', 'Name: Z to A'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Sort By',
        initial='date'
    )


class ServiceRatingForm(forms.ModelForm):
    """
    Form for customers to rate and review services after completion
    """
    
    class Meta:
        model = ServiceRequest
        fields = ['rating', 'review']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
            'review': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your experience with this service (optional)',
                'rows': 4
            }),
        }
        labels = {
            'rating': 'Rating',
            'review': 'Review (Optional)',
        }
        help_texts = {
            'rating': 'Rate your experience from 1 to 5 stars',
            'review': 'Help other customers by sharing your experience',
        }
    
    def clean_rating(self):
        """Validate rating is within valid range"""
        rating = self.cleaned_data.get('rating')
        if rating < 1 or rating > 5:
            raise ValidationError("Rating must be between 1 and 5")
        return rating