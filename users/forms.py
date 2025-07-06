from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import User, Customer, Company


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
    """
    Company registration form with email, username, field of work,
    password, and password confirmation fields.
    Includes validation for unique email and username.
    """
    email = forms.EmailField(
        max_length=100,
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your company email address',
            'class': 'form-control'
        }),
        help_text='Enter a valid company email address.'
    )

    field_of_work = forms.ChoiceField(
        choices=[
            ('', 'Select your field of work'),
            ('Air Conditioner', 'Air Conditioner'),
            ('All in One', 'All in One'),
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
        ],
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text='Select your primary field of work.'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'field_of_work', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize username field
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Enter your company username',
            'class': 'form-control'
        })
        self.fields['username'].help_text = 'Enter a unique company username.'

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
        """Save the user and create associated Company profile."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_company = True

        if commit:
            user.save()
            # Create Company profile
            Company.objects.create(
                user=user,
                field=self.cleaned_data['field_of_work']
            )
        return user


class UserLoginForm(forms.Form):
    """User login form supporting both email and username authentication."""
    email_or_username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Email or Username',
            'class': 'form-control'
        }),
        help_text='You can login with either your email address or username.'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter Password',
            'class': 'form-control'
        })
    )

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['email_or_username'].widget.attrs['autocomplete'] = 'username'
        self.fields['password'].widget.attrs['autocomplete'] = 'current-password'

    def clean(self):
        """Validate the login credentials."""
        cleaned_data = super().clean()
        email_or_username = cleaned_data.get('email_or_username')
        password = cleaned_data.get('password')

        if email_or_username and password:
            # Try to find user by email first, then by username
            user = None
            try:
                # Check if input looks like an email
                if '@' in email_or_username:
                    user = User.objects.get(email=email_or_username)
                else:
                    user = User.objects.get(username=email_or_username)
            except User.DoesNotExist:
                raise forms.ValidationError('Invalid email/username or password.')

            # Store the found user for use in the view
            cleaned_data['user_obj'] = user

        return cleaned_data
