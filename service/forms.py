from django import forms
from .models import Service, ServiceRequest,ServiceRating
from django.utils import timezone

class CreateNewService(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price_hour', 'field']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get the user from kwargs
        super(CreateNewService, self).__init__(*args, **kwargs)
        
        #   # Add date_created as a read-only field
        # self.fields['date_created'] = forms.DateTimeField(
        #     required=False,
        #     disabled=True,
        #     initial=timezone.now(),  # Set the initial value to the current time
        #     widget=forms.DateTimeInput(attrs={'readonly': 'readonly'})
        # )

        # adding placeholders to form fields
        self.fields['name'].widget.attrs['placeholder'] = 'Enter Service Name'
        self.fields['description'].widget.attrs['placeholder'] = 'Enter Description'
        self.fields['price_hour'].widget.attrs['placeholder'] = 'Enter Price per Hour'
        self.fields['name'].widget.attrs['autocomplete'] = 'off'
        # Filter field choices based on the user's company
        if user and hasattr(user, 'company'):
            company_field=user.company.field
            if company_field != 'All in One':
                #Show only the company's field
                self.fields['field'].choices=[(company_field,company_field)]
            else:
                # Keep all available choices if 'All in One'
                self.fields['field'].choices = Service.FIELD_CHOICES
                

class RequestServiceForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['address', 'service_time']

    def __init__(self, *args, **kwargs):
        super(RequestServiceForm, self).__init__(*args, **kwargs)
        self.fields['address'].widget.attrs['placeholder'] = 'Enter Address'
        self.fields['service_time'].widget.attrs['placeholder'] = 'Enter Service Time (hours)'
        
class ServiceRatingForm(forms.ModelForm):
    class Meta:
        model = ServiceRating
        fields = ['rating', 'review']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),  # Display radio buttons for ratings
        }