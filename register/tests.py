from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class UserRegistrationTest(TestCase):
    """Test cases for user registration functionality"""
    
    def test_register_page_loads(self):
        """Test if registration page loads correctly"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register/register.html')
    
    def test_user_registration(self):
        """Test if a user can register successfully"""
        # Post registration data
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPassword123',
            'password2': 'TestPassword123',
            'first_name': 'Test',
            'last_name': 'User',
        })
        
        # Check if user was created
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        
        # Check if redirected to login page after registration
        self.assertRedirects(response, reverse('login'))


class UserLoginTest(TestCase):
    """Test cases for user login functionality"""
    
    def setUp(self):
        """Set up a test user"""
        self.credentials = {
            'username': 'testuser',
            'password': 'TestPassword123'
        }
        User.objects.create_user(**self.credentials)
    
    def test_login_page_loads(self):
        """Test if login page loads correctly"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register/login.html')
    
    def test_user_login(self):
        """Test if a user can login successfully"""
        response = self.client.post(reverse('login'), self.credentials, follow=True)
        # Check if user is logged in
        self.assertTrue(response.context['user'].is_authenticated)
        # Check if redirected to home page after login
        self.assertRedirects(response, reverse('home')) 