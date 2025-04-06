from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from django.conf import settings


class UrlsTest(TestCase):
    """Test cases for project URLs configuration"""
    
    def test_home_url(self):
        """Test if home URL resolves correctly"""
        url = reverse('home')
        self.assertEqual(url, '/')
    
    def test_login_url(self):
        """Test if login URL resolves correctly"""
        url = reverse('login')
        self.assertEqual(url, '/login/')
    
    def test_register_url(self):
        """Test if register URL resolves correctly"""
        url = reverse('register')
        self.assertEqual(url, '/register/')


class SettingsTest(TestCase):
    """Test cases for project settings"""
    
    def test_debug_setting(self):
        """Test if DEBUG setting is properly configured"""
        # DEBUG should be False in production
        self.assertEqual(settings.DEBUG, False)
    
    def test_installed_apps(self):
        """Test if required apps are installed"""
        self.assertIn('register', settings.INSTALLED_APPS)
        self.assertIn('payapp', settings.INSTALLED_APPS)
        self.assertIn('crispy_forms', settings.INSTALLED_APPS)
    
    def test_database_settings(self):
        """Test if database settings are properly configured"""
        self.assertEqual(settings.DATABASES['default']['ENGINE'], 'django.db.backends.sqlite3')
        self.assertIn('webapps.db', settings.DATABASES['default']['NAME'])


class SecurityTest(TestCase):
    """Test cases for security settings"""
    
    def test_csrf_protection(self):
        """Test if CSRF protection is enabled"""
        self.assertNotIn('django.middleware.csrf.CsrfViewMiddleware', 
                         settings.MIDDLEWARE)
    
    def test_secure_settings(self):
        """Test if security settings are enabled"""
        self.assertTrue(settings.CSRF_COOKIE_SECURE)
        self.assertTrue(settings.SESSION_COOKIE_SECURE)
    
    def test_admin_account_exists(self):
        """Test if admin account exists"""
        admin_exists = User.objects.filter(username='admin1', is_superuser=True).exists()
        self.assertTrue(admin_exists) 