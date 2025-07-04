from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import User, Customer


class DateInput(forms.DateInput):
    input_type = 'date'


def validate_email(value):
    # In case the email already exists in an email input in a registration form, this function is fired
    if User.objects.filter(email=value).exists():
        raise ValidationError(
            value + " is already taken.")


class CustomerSignUpForm(UserCreationForm):
    """
    Customer registration form with email, username, date of birth,
    password, and password confirmation fields.
    Includes validation for unique email and username.
    """
    email = forms.EmailField(
        max_length=100,
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email address',
            'class': 'form-control'
        }),
        help_text='Enter a valid email address.'
    )

    birth_date = forms.DateField(
        required=True,
        widget=DateInput(attrs={
            'placeholder': 'Select your date of birth',
            'class': 'form-control'
        }),
        help_text='Select your date of birth.'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'birth_date', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize username field
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Enter your username',
            'class': 'form-control'
        })
        self.fields['username'].help_text = 'Enter a unique username.'

        # Customize password fields
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Enter your password',
            'class': 'form-control'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm your password',
            'class': 'form-control'
        })

    def clean_username(self):
        """Validate that the username is unique."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError(f'Username "{username}" is already taken.')
        return username

    def clean_email(self):
        """Validate that the email is unique."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(f'Email "{email}" is already registered.')
        return email

    @transaction.atomic
    def save(self, commit=True):
        """Save the user and create associated Customer profile."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_customer = True

        if commit:
            user.save()
            # Create Customer profile
            Customer.objects.create(
                user=user,
                birth=self.cleaned_data['birth_date']
            )
        return user


class CompanySignUpForm(UserCreationForm):
    pass


class UserLoginForm(forms.Form):
    """User login form using email and password."""
    email = forms.EmailField(widget=forms.TextInput(
        attrs={'placeholder': 'Enter Email', 'class': 'form-control'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password', 'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['autocomplete'] = 'off'
