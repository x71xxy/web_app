from django.db import models
from django.contrib.auth.models import User
# from django.db.models.signals import post_save
# from django.dispatch import receiver
from register.models import UserProfile

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account')
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    
    def __str__(self):
        return f"{self.user.username}'s account ({self.balance} {self.currency})"

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('PAYMENT', 'Payment'),
        ('REQUEST', 'Payment Request'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected'),
    ]
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_transactions')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    sender_currency = models.CharField(max_length=3)
    receiver_currency = models.CharField(max_length=3)
    converted_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        base_str = f"{self.get_transaction_type_display()} from {self.sender.username} to {self.receiver.username} ({self.amount} {self.sender_currency})"
        if self.converted_amount and self.sender_currency != self.receiver_currency:
            return f"{base_str} → {self.converted_amount} {self.receiver_currency}"
        return base_str

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    message = models.TextField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.message:
            return f"Notification for {self.user.username}: {self.message[:30]}..."
        return f"Notification for {self.user.username} about transaction {self.transaction.id}"

# Uncomment to enable signal handlers
# @receiver(post_save, sender=User)
# def create_account(sender, instance, created, **kwargs):
#     """Create an account for new users"""
#     if created:
#         # Set initial balance (£750 or equivalent)
#         initial_amount = 750.00
        
#         # Convert initial amount based on selected currency
#         if hasattr(instance, 'profile') and instance.profile.currency == 'USD':
#             initial_amount = 750 * 1.30  # Sample exchange rate
#         elif hasattr(instance, 'profile') and instance.profile.currency == 'EUR':
#             initial_amount = 750 * 1.17  # Sample exchange rate
        
#         Account.objects.create(
#             user=instance,
#             balance=initial_amount,
#             currency=instance.profile.currency if hasattr(instance, 'profile') else 'GBP'
#         ) 