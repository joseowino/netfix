from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from .models import User, Customer, Company
from .forms import CustomerSignUpForm, CompanySignUpForm, UserLoginForm
from datetime import date, timedelta

class UserModelTests(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_user_creation(self):
        """Test creating a basic user"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))
        self.assertFalse(self.user.is_customer)
        self.assertFalse(self.user.is_company)

    def test_user_str_method(self):
        """Test string representation of User"""
        self.assertEqual(str(self.user), 'testuser')

class CustomerModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testcustomer',
            email='customer@test.com',
            password='testpass123',
            is_customer=True
        )
        self.customer = Customer.objects.create(
            user=self.user,
            date_of_birth=date(2000, 1, 1)
        )

    def test_customer_creation(self):
        """Test creating a customer profile"""
        self.assertEqual(self.customer.user.username, 'testcustomer')
        self.assertTrue(self.customer.user.is_customer)
        self.assertEqual(self.customer.date_of_birth, date(2000, 1, 1))

    def test_customer_str_method(self):
        """Test string representation of Customer"""
        self.assertEqual(str(self.customer), 'testcustomer')

class CompanyModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testcompany',
            email='company@test.com',
            password='testpass123',
            is_company=True
        )
        self.company = Company.objects.create(
            user=self.user,
            field='Plumbing',
            description='Test company description'
        )

    def test_company_creation(self):
        """Test creating a company profile"""
        self.assertEqual(self.company.user.username, 'testcompany')
        self.assertTrue(self.company.user.is_company)
        self.assertEqual(self.company.field, 'Plumbing')
        self.assertEqual(self.company.description, 'Test company description')

    def test_company_str_method(self):
        """Test string representation of Company"""
        self.assertEqual(str(self.company), 'testcompany')

class CustomerSignUpFormTests(TestCase):
    def setUp(self):
        self.valid_data = {
            'username': 'newcustomer',
            'email': 'newcustomer@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'date_of_birth': date(2000, 1, 1)
        }

    def test_valid_form(self):
        """Test form with valid data"""
        form = CustomerSignUpForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_invalid_age(self):
        """Test form with invalid age (too young)"""
        data = self.valid_data.copy()
        data['date_of_birth'] = timezone.now().date()
        form = CustomerSignUpForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('date_of_birth', form.errors)

    def test_duplicate_email(self):
        """Test form with duplicate email"""
        User.objects.create_user(
            username='existing',
            email=self.valid_data['email'],
            password='testpass123'
        )
        form = CustomerSignUpForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

class CompanySignUpFormTests(TestCase):
    def setUp(self):
        self.valid_data = {
            'username': 'newcompany',
            'email': 'newcompany@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'field': 'Plumbing',
            'description': 'Test description'
        }

    def test_valid_form(self):
        """Test form with valid data"""
        form = CompanySignUpForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_invalid_field(self):
        """Test form with invalid field choice"""
        data = self.valid_data.copy()
        data['field'] = 'InvalidField'
        form = CompanySignUpForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('field', form.errors)

class UserViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('users:register')
        self.login_url = reverse('users:login')
        self.customer_signup_url = reverse('users:register_customer')
        self.company_signup_url = reverse('users:register_company')

        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

    def test_register_page_load(self):
        """Test register page loads correctly"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_login_page_load(self):
        """Test login page loads correctly"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_customer_signup(self):
        """Test customer signup process"""
        data = {
            'username': 'newcustomer',
            'email': 'newcustomer@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'date_of_birth': '2000-01-01'
        }
        response = self.client.post(self.customer_signup_url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful signup
        self.assertTrue(User.objects.filter(username='newcustomer').exists())
        user = User.objects.get(username='newcustomer')
        self.assertTrue(user.is_customer)

    def test_company_signup(self):
        """Test company signup process"""
        data = {
            'username': 'newcompany',
            'email': 'newcompany@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'field': 'Plumbing',
            'description': 'Test company'
        }
        response = self.client.post(self.company_signup_url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful signup
        self.assertTrue(User.objects.filter(username='newcompany').exists())
        user = User.objects.get(username='newcompany')
        self.assertTrue(user.is_company)

    def test_login_valid_credentials(self):
        """Test login with valid credentials"""
        data = {
            'email': 'test@test.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful login

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {
            'email': 'test@test.com',
            'password': 'wrongpass'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

class EmailBackendTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

    def test_authenticate_valid_credentials(self):
        """Test authentication with valid email and password"""
        user = authenticate(None, email='test@test.com', password='testpass123')
        self.assertIsNotNone(user)
        self.assertEqual(user, self.user)

    def test_authenticate_invalid_credentials(self):
        """Test authentication with invalid credentials"""
        user = authenticate(None, email='test@test.com', password='wrongpass')
        self.assertIsNone(user)

        user = authenticate(None, email='wrong@test.com', password='testpass123')
        self.assertIsNone(user)
