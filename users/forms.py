from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import User, Company, Customer

class DateInput(forms.DateInput):
    input_type = 'date'

def validate_email(value):
    if User.objects.filter(email=value).exists():
        raise ValidationError(value + " is already taken.")
    
class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['profile_image']
        widgets = {
            'profile_image':  forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }
    def __init__(self, *args, **kwargs):
        # Dynamically set the model to either Customer or Company based on the instance provided
        instance = kwargs.get('instance')
        if instance and isinstance(instance, Customer):
            self.Meta.model = Customer
        elif instance and isinstance(instance, Company):
            self.Meta.model = Company
        super().__init__(*args, **kwargs)


class CustomerSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, validators=[validate_email])
    birth = forms.DateField(widget=DateInput, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'birth', 'password1', 'password2',]
        profile_image = forms.ImageField(required=False)

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_customer = True
        if commit:
            user.save()
            customer=Customer.objects.create(user=user, birth=self.cleaned_data.get('birth'))
             # Save the profile image if it was provided
            if self.cleaned_data.get('profile_image'):
                customer.profile_image = self.cleaned_data.get('profile_image')
                customer.save()
        return user

class CompanySignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, validators=[validate_email])
    field = forms.ChoiceField(choices=Company.FIELD_CHOICES, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'field', 'password1', 'password2']

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_company = True
        if commit:
            user.save()
            Company.objects.create(user=user, field=self.cleaned_data.get('field'))
        return user

class UserLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Enter Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password'}))

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['autocomplete'] = 'off'