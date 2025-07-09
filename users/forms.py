from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.core.exceptions import ValidationError

from datetime import date
from .models import User, Company, Customer


class DateInput(forms.DateInput):
    input_type = 'date'


def validate_email(value):
    # In case the email already exists in an email input in a registration form, this function is fired
    if User.objects.filter(email=value).exists():
        raise ValidationError(
            value + " is already taken.")


class CustomerSignUpForm(UserCreationForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
        label='Date of Birth',
        help_text="You must be at least 15 years old to register"
    )

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if not dob:
            raise forms.ValidationError("Date of birth is required.")
            
        today = date.today()
        
        # Check if birth date is in the future
        if dob > today:
            raise forms.ValidationError("Birth date cannot be in the future.")
            
        # Calculate age
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        
        # Check minimum age (15 years)
        if age < 15:
            raise forms.ValidationError("You must be at least 15 years old to register.")
            
        # Check maximum age (120 years)
        if age > 120:
            raise forms.ValidationError("Please enter a valid birth date.")
            
        return dob

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'date_of_birth']
        labels = {
            'username': 'Username',
            'email': 'Email Address',
            'password1': 'Password',
            'password2': 'Confirm Password',
            'date_of_birth': 'Date of Birth'
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        validate_email(email)
        return email
    
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already taken.")
        return username
    
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_customer = True
        user.save()
        # Create Customer instance after the user instance is saved
        Customer.objects.create(user=user, date_of_birth=self.cleaned_data['date_of_birth'])
        return user

class CompanySignUpForm(UserCreationForm):
    field = forms.ChoiceField(choices=Company.FIELD_CHOICES)
    image = forms.ImageField(required=False)
    description = forms.CharField(widget=forms.Textarea, max_length=500, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self):
        user = super().save(commit=False)
        user.is_company = True
        user.save()
        Company.objects.create(
            user=user,
            field=self.cleaned_data['field'],
            image=self.cleaned_data.get('image'),
            description=self.cleaned_data.get('description', '')
        )
        return user
    def clean_email(self):
        email = self.cleaned_data.get('email')
        validate_email(email)
        return email
    
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already taken.")
        return username


class UserLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(
        attrs={'placeholder': 'Enter Email'}), label='Email')
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password', 'label': 'Email'}))

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['autocomplete'] = 'off'
