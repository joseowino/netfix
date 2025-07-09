
from django.test import TestCase
from django.utils import timezone
from users.models import User, Company, Customer
from .models import Service, ServiceRequest, Review
from decimal import Decimal

class ServiceModelTests(TestCase):
    def setUp(self):
        # Create company user and company
        self.company_user = User.objects.create_user(
            username='testcompany',
            password='testpass123',
            email='company@test.com',
            is_company=True
        )
        self.company = Company.objects.create(
            user=self.company_user,
            field='Plumbing'
        )
        
        # Create customer user and customer
        self.customer_user = User.objects.create_user(
            username='testcustomer',
            password='testpass123',
            email='customer@test.com',
            is_customer=True
        )
        self.customer = Customer.objects.create(
            user=self.customer_user,
            date_of_birth=timezone.now().date()
        )
        
        # Create test service
        self.service = Service.objects.create(
            company=self.company,
            name='Test Plumbing Service',
            description='Test Description',
            price_hour=Decimal('50.00'),
            field='Plumbing'
        )

    def test_service_creation(self):
        """Test that a service can be created with all fields"""
        self.assertEqual(self.service.name, 'Test Plumbing Service')
        self.assertEqual(self.service.description, 'Test Description')
        self.assertEqual(self.service.price_hour, Decimal('50.00'))
        self.assertEqual(self.service.field, 'Plumbing')
        self.assertEqual(self.service.rating, 1)  # Default rating
        self.assertEqual(self.service.company, self.company)

    def test_service_str_method(self):
        """Test the string representation of a Service"""
        self.assertEqual(str(self.service), 'Test Plumbing Service')

    def test_get_request_count(self):
        """Test the get_request_count method"""
        # Create some service requests
        ServiceRequest.objects.create(
            service=self.service,
            customer=self.customer,
            requested_date=timezone.now() + timezone.timedelta(days=1),
            status='PENDING'
        )
        ServiceRequest.objects.create(
            service=self.service,
            customer=self.customer,
            requested_date=timezone.now() + timezone.timedelta(days=2),
            status='ACCEPTED'
        )
        
        self.assertEqual(self.service.get_request_count(), 2)

    def test_get_most_requested(self):
        """Test the get_most_requested static method"""
        # Create another service with more requests
        popular_service = Service.objects.create(
            company=self.company,
            name='Popular Service',
            description='Popular Description',
            price_hour=Decimal('75.00'),
            field='Plumbing'
        )
        
        # Create multiple requests for popular service
        for i in range(3):
            ServiceRequest.objects.create(
                service=popular_service,
                customer=self.customer,
                requested_date=timezone.now() + timezone.timedelta(days=i+1),
                status='PENDING'
            )
        
        # Create one request for original service
        ServiceRequest.objects.create(
            service=self.service,
            customer=self.customer,
            requested_date=timezone.now() + timezone.timedelta(days=1),
            status='PENDING'
        )
        
        most_requested = Service.get_most_requested(limit=2)
        self.assertEqual(most_requested[0], popular_service)
        self.assertEqual(most_requested[1], self.service)

class ServiceRequestModelTests(TestCase):
    def setUp(self):
        # Create company user and company
        self.company_user = User.objects.create_user(
            username='testcompany',
            password='testpass123',
            email='company@test.com',
            is_company=True
        )
        self.company = Company.objects.create(
            user=self.company_user,
            field='Plumbing'
        )
        
        # Create customer user and customer
        self.customer_user = User.objects.create_user(
            username='testcustomer',
            password='testpass123',
            email='customer@test.com',
            is_customer=True
        )
        self.customer = Customer.objects.create(
            user=self.customer_user,
            date_of_birth=timezone.now().date()
        )
        
        # Create test service
        self.service = Service.objects.create(
            company=self.company,
            name='Test Plumbing Service',
            description='Test Description',
            price_hour=Decimal('50.00'),
            field='Plumbing'
        )

    def test_service_request_creation(self):
        """Test creating a service request with all fields"""
        request = ServiceRequest.objects.create(
            service=self.service,
            customer=self.customer,
            requested_date=timezone.now() + timezone.timedelta(days=1),
            address='123 Test St',
            hours_needed=2,
            notes='Test notes',
            status='PENDING'
        )
        
        self.assertEqual(request.service, self.service)
        self.assertEqual(request.customer, self.customer)
        self.assertEqual(request.address, '123 Test St')
        self.assertEqual(request.hours_needed, 2)
        self.assertEqual(request.notes, 'Test notes')
        self.assertEqual(request.status, 'PENDING')
        self.assertEqual(request.total_cost, Decimal('100.00'))  # 50.00 * 2 hours

    def test_service_request_total_cost_calculation(self):
        """Test that total cost is calculated correctly on save"""
        request = ServiceRequest.objects.create(
            service=self.service,
            customer=self.customer,
            requested_date=timezone.now() + timezone.timedelta(days=1),
            hours_needed=3,
            status='PENDING'
        )
        
        self.assertEqual(request.total_cost, Decimal('150.00'))  # 50.00 * 3 hours

class ReviewModelTests(TestCase):
    def setUp(self):
        # Create company user and company
        self.company_user = User.objects.create_user(
            username='testcompany',
            password='testpass123',
            email='company@test.com',
            is_company=True
        )
        self.company = Company.objects.create(
            user=self.company_user,
            field='Plumbing'
        )
        
        # Create customer user and customer
        self.customer_user = User.objects.create_user(
            username='testcustomer',
            password='testpass123',
            email='customer@test.com',
            is_customer=True
        )
        self.customer = Customer.objects.create(
            user=self.customer_user,
            date_of_birth=timezone.now().date()
        )
        
        # Create test service
        self.service = Service.objects.create(
            company=self.company,
            name='Test Plumbing Service',
            description='Test Description',
            price_hour=Decimal('50.00'),
            field='Plumbing'
        )
        
        # Create service request
        self.service_request = ServiceRequest.objects.create(
            service=self.service,
            customer=self.customer,
            requested_date=timezone.now() + timezone.timedelta(days=1),
            status='COMPLETED'
        )

    def test_review_creation_and_rating_update(self):
        """Test creating a review and updating service/company ratings"""
        review = Review.objects.create(
            service_request=self.service_request,
            service=self.service,
            customer=self.customer,
            rating=5,
            comment='Excellent service'
        )
        
        # Refresh service and company from database
        self.service.refresh_from_db()
        self.company.refresh_from_db()
        
        # Check if ratings were updated
        self.assertEqual(self.service.rating, 5)
        self.assertEqual(self.company.rating, 5)

    def test_multiple_reviews_average_rating(self):
        """Test that multiple reviews correctly average the rating"""
        # Create another customer and service request
        customer2 = Customer.objects.create(
            user=User.objects.create_user(
                username='testcustomer2',
                password='testpass123',
                email='customer2@test.com',
                is_customer=True
            ),
            date_of_birth=timezone.now().date()
        )
        
        service_request2 = ServiceRequest.objects.create(
            service=self.service,
            customer=customer2,
            requested_date=timezone.now() + timezone.timedelta(days=1),
            status='COMPLETED'
        )
        
        # Create two reviews with different ratings
        Review.objects.create(
            service_request=self.service_request,
            service=self.service,
            customer=self.customer,
            rating=5,
            comment='Excellent service'
        )
        
        Review.objects.create(
            service_request=service_request2,
            service=self.service,
            customer=customer2,
            rating=3,
            comment='Good service'
        )
        
        # Refresh service and company from database
        self.service.refresh_from_db()
        self.company.refresh_from_db()
        
        # Check if ratings were averaged correctly (rounded to nearest integer)
        self.assertEqual(self.service.rating, 4)  # (5 + 3) / 2 = 4
        self.assertEqual(self.company.rating, 4)

