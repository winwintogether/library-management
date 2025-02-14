# library/tests.py
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import User, Book, Loan

class BookTests(APITestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_admin=True
        )
        
        # Create regular user
        self.regular_user = User.objects.create_user(
            username='user',
            password='user123',
            is_admin=False
        )
        
        # Create test book
        self.test_book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890123',
            page_count=200,
            quantity=5,
            available_quantity=5
        )

    def test_create_book_as_admin(self):
        """Test creating a book as admin user"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('book-list')
        data = {
            'title': 'New Book',
            'author': 'New Author',
            'isbn': '9876543210123',
            'page_count': 300,
            'quantity': 3,
            'available_quantity': 3
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)
        self.assertEqual(Book.objects.get(isbn='9876543210123').title, 'New Book')

    def test_create_book_as_regular_user(self):
        """Test that regular users cannot create books"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('book-list')
        data = {
            'title': 'New Book',
            'author': 'New Author',
            'isbn': '9876543210123',
            'page_count': 300,
            'quantity': 3,
            'available_quantity': 3
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_books_anonymous(self):
        """Test that anonymous users can list books"""
        url = reverse('book-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

class LoanTests(APITestCase):
    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_admin=True
        )
        
        self.user1 = User.objects.create_user(
            username='user1',
            password='user123',
            is_admin=False
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            password='user123',
            is_admin=False
        )
        
        # Create test book
        self.test_book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890123',
            page_count=200,
            quantity=3,
            available_quantity=3
        )

    def test_borrow_book_authenticated(self):
        """Test borrowing a book as authenticated user"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('loan-list')

        data = {
            'return_date': timezone.now(),
            'book': self.test_book.id,
        }
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Loan.objects.count(), 1)
        self.assertEqual(Book.objects.get(id=self.test_book.id).available_quantity, 2)

    def test_borrow_book_unauthenticated(self):
        """Test that unauthenticated users cannot borrow books"""
        url = reverse('loan-list')
        data = {
            'return_date': timezone.now(),
            'book': self.test_book.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_borrow_unavailable_book(self):
        """Test borrowing a book with no available copies"""
        self.test_book.available_quantity = 0
        self.test_book.save()
        
        self.client.force_authenticate(user=self.user1)
        url = reverse('loan-list')
        data = {
            'return_date': timezone.now(),
            'book': self.test_book.id,
        }
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Loan.objects.count(), 0)

    def test_loan_list(self):
        """Test that admins can only see all loans"""
        # Create loans for both users
        loan1 = Loan.objects.create(
            user=self.user1,
            book=self.test_book,
            borrowed_date=timezone.now()
        )
        loan2 = Loan.objects.create(
            user=self.user2,
            book=self.test_book,
            borrowed_date=timezone.now()
        )
        
        # Test regular user can only see their loans
        url = reverse('loan-list')

        # Test admin can see all loans
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url)
        self.assertEqual(len(response.data['results']), 2)

    def test_concurrent_borrows(self):
        """Test that multiple users can borrow different copies of the same book"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('loan-list')
        data = {
            'return_date': timezone.now(),
            'book': self.test_book.id,
        }
        response1 = self.client.post(url, data, format="json")
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        self.client.force_authenticate(user=self.user2)
        data = {
            'return_date': timezone.now(),
            'book': self.test_book.id,
        }
        response2 = self.client.post(url, data, format="json")
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        
        self.assertEqual(Book.objects.get(id=self.test_book.id).available_quantity, 1)
        self.assertEqual(Loan.objects.count(), 2)

class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890123',
            page_count=200,
            quantity=5,
            available_quantity=5
        )

    def test_book_str_representation(self):
        """Test the string representation of Book model"""
        self.assertEqual(str(self.book), 'Test Book by Test Author')

    def test_loan_str_representation(self):
        """Test the string representation of Loan model"""
        loan = Loan.objects.create(
            user=self.user,
            book=self.book
        )
        self.assertEqual(str(loan), 'testuser - Test Book')
