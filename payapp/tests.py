from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Transaction, PaymentRequest, Account
from decimal import Decimal


class AccountModelTest(TestCase):
    """Test cases for Account model"""
    
    def setUp(self):
        """Set up test user and account"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123'
        )
        self.account = Account.objects.create(
            user=self.user,
            currency='GBP',
            balance=Decimal('750.00')
        )
    
    def test_account_creation(self):
        """Test if account is created correctly"""
        self.assertEqual(self.account.user.username, 'testuser')
        self.assertEqual(self.account.currency, 'GBP')
        self.assertEqual(self.account.balance, Decimal('750.00'))


class TransactionTest(TestCase):
    """Test cases for transaction functionality"""
    
    def setUp(self):
        """Set up test users and accounts"""
        # Create sender
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@example.com',
            password='SenderPass123'
        )
        self.sender_account = Account.objects.create(
            user=self.sender,
            currency='GBP',
            balance=Decimal('1000.00')
        )
        
        # Create recipient
        self.recipient = User.objects.create_user(
            username='recipient',
            email='recipient@example.com',
            password='RecipientPass123'
        )
        self.recipient_account = Account.objects.create(
            user=self.recipient,
            currency='GBP',
            balance=Decimal('500.00')
        )
    
    def test_send_payment(self):
        """Test if payment is processed correctly"""
        # Login as sender
        self.client.login(username='sender', password='SenderPass123')
        
        # Send payment
        response = self.client.post(reverse('send_payment'), {
            'recipient_email': 'recipient@example.com',
            'amount': '100.00',
            'description': 'Test payment'
        })
        
        # Refresh account data from database
        self.sender_account.refresh_from_db()
        self.recipient_account.refresh_from_db()
        
        # Check balances are updated
        self.assertEqual(self.sender_account.balance, Decimal('900.00'))
        self.assertEqual(self.recipient_account.balance, Decimal('600.00'))
        
        # Check transaction record exists
        transaction = Transaction.objects.get(sender=self.sender, recipient=self.recipient)
        self.assertEqual(transaction.amount, Decimal('100.00'))
        self.assertEqual(transaction.description, 'Test payment')


class PaymentRequestTest(TestCase):
    """Test cases for payment request functionality"""
    
    def setUp(self):
        """Set up test users and accounts"""
        # Create requester
        self.requester = User.objects.create_user(
            username='requester',
            email='requester@example.com',
            password='RequesterPass123'
        )
        self.requester_account = Account.objects.create(
            user=self.requester,
            currency='GBP',
            balance=Decimal('300.00')
        )
        
        # Create payer
        self.payer = User.objects.create_user(
            username='payer',
            email='payer@example.com',
            password='PayerPass123'
        )
        self.payer_account = Account.objects.create(
            user=self.payer,
            currency='GBP',
            balance=Decimal('1000.00')
        )
    
    def test_request_payment(self):
        """Test if payment request is created correctly"""
        # Login as requester
        self.client.login(username='requester', password='RequesterPass123')
        
        # Create payment request
        response = self.client.post(reverse('request_payment'), {
            'payer_email': 'payer@example.com',
            'amount': '200.00',
            'description': 'Test request'
        })
        
        # Check payment request record exists
        request = PaymentRequest.objects.get(requester=self.requester, payer=self.payer)
        self.assertEqual(request.amount, Decimal('200.00'))
        self.assertEqual(request.description, 'Test request')
        self.assertEqual(request.status, 'pending') 