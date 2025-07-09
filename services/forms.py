from django import forms
from .models import Company, Review
from django.utils import timezone
from datetime import timedelta


class CreateNewService(forms.Form):
    name = forms.CharField(max_length=40, widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), label='Description')
    price_hour = forms.DecimalField(
        decimal_places=2, 
        max_digits=5, 
        min_value=0.00,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    field = forms.ChoiceField(
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        if company:
            if company.field == 'All in One':
                self.fields['field'].choices = Company.FIELD_CHOICES
            else:
                self.fields['field'].choices = [(company.field, company.field)]
                self.fields['field'].widget.attrs['readonly'] = True
                self.fields['field'].initial = company.field

        # Add placeholders
        self.fields['name'].widget.attrs['placeholder'] = 'Enter Service Name'
        self.fields['description'].widget.attrs['placeholder'] = 'Enter Description'
        self.fields['price_hour'].widget.attrs['placeholder'] = 'Enter Price per Hour'
        self.fields['name'].widget.attrs['autocomplete'] = 'off'


class RequestServiceForm(forms.Form):
    address = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    hours_needed = forms.IntegerField(
        min_value=1,
        max_value=24,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    requested_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }
        )
    )
    notes = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'placeholder': 'Add any special requirements or notes here...',
                'rows': 4
            }
        ),
        required=False
    )

    def clean_requested_date(self):
        requested_date = self.cleaned_data['requested_date']
        now = timezone.now()
        
        if requested_date < now:
            raise forms.ValidationError("Requested date cannot be in the past")
        
        if requested_date > now + timedelta(days=30):
            raise forms.ValidationError("Requested date cannot be more than 30 days in the future")
            
        return requested_date


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '5'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience with this service...'
            })
        }
