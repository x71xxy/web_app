from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Account, Transaction, Notification
from .forms import PaymentForm, RequestForm
import requests
from decimal import Decimal
import logging
from django.core.paginator import Paginator
from django.db.models import Q

# Configure logger
logger = logging.getLogger(__name__)

def debug_transaction(transaction_obj, action="Created"):
    """Log transaction details in a pre-formatted way for easier debugging"""
    debug_info = f"""
Transaction Debug Info ({action}):
--------------------------------
ID: {transaction_obj.id}
Type: {transaction_obj.transaction_type}
Status: {transaction_obj.status}
Sender: {transaction_obj.sender.username} ({transaction_obj.sender.email})
Receiver: {transaction_obj.receiver.username} ({transaction_obj.receiver.email})
Amount: {transaction_obj.amount} {transaction_obj.sender_currency}
"""
    if transaction_obj.converted_amount and transaction_obj.sender_currency != transaction_obj.receiver_currency:
        debug_info += f"Conversion: {transaction_obj.amount} {transaction_obj.sender_currency} → {transaction_obj.converted_amount} {transaction_obj.receiver_currency}\n"
    
    debug_info += f"Date: {transaction_obj.timestamp}\n"
    
    logger.debug(debug_info)
    print(debug_info)  # Also print to console for development

@login_required
def dashboard_view(request):
    # Get user account information
    account = request.user.account
    
    # Get recent transactions
    transactions = Transaction.objects.filter(
        sender=request.user
    ) | Transaction.objects.filter(
        receiver=request.user
    ).order_by('-timestamp')[:5]
    
    # Get unread notifications
    notifications = Notification.objects.filter(
        user=request.user, 
        is_read=False
    ).order_by('-timestamp')[:5]
    
    context = {
        'account': account,
        'transactions': transactions,
        'notifications': notifications,
        'unread_count': notifications.count()
    }
    
    return render(request, 'payapp/dashboard.html', context)

@login_required
def send_payment_view(request):
    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            recipient_email = form.cleaned_data.get('recipient_email')
            amount = form.cleaned_data.get('amount')
            
            try:
                # Verify recipient exists
                recipient = User.objects.get(email=recipient_email)
                
                # Check for sufficient funds
                sender_account = request.user.account
                if sender_account.balance < amount:
                    messages.error(request, "Insufficient funds in your account.")
                    return render(request, 'payapp/send_payment.html', {'form': form})
                
                # Prevent sending to yourself
                if recipient == request.user:
                    messages.error(request, "You cannot send money to yourself.")
                    return render(request, 'payapp/send_payment.html', {'form': form})
                
                with transaction.atomic():
                    # Calculate converted amount if currencies are different
                    recipient_account = recipient.account
                    converted_amount = amount
                    
                    if sender_account.currency != recipient_account.currency:
                        # Convert the currency
                        converted_amount = convert_currency(
                            sender_account.currency,
                            recipient_account.currency,
                            amount
                        )
                    
                    # Create transaction
                    transaction_obj = Transaction.objects.create(
                        sender=request.user,
                        receiver=recipient,
                        amount=amount,
                        sender_currency=sender_account.currency,
                        receiver_currency=recipient_account.currency,
                        converted_amount=converted_amount if sender_account.currency != recipient_account.currency else None,
                        transaction_type='PAYMENT',
                        status='COMPLETED'
                    )
                    
                    # Log transaction details
                    debug_transaction(transaction_obj, "Payment Sent")
                    
                    # Update sender's balance
                    sender_account.balance -= amount
                    sender_account.save()
                    
                    # Update recipient's balance
                    recipient_account.balance += converted_amount
                    recipient_account.save()
                    
                    # Create notification for recipient
                    Notification.objects.create(
                        user=recipient,
                        transaction=transaction_obj,
                        is_read=False
                    )
                    
                    # Create notification for sender as well
                    Notification.objects.create(
                        user=request.user,
                        transaction=transaction_obj,
                        is_read=False
                    )
                
                messages.success(request, f"Successfully sent {amount} {sender_account.currency} to {recipient_email}.")
                return redirect('dashboard')
                
            except User.DoesNotExist:
                messages.error(request, "User with this email does not exist.")
    else:
        form = PaymentForm()
    
    return render(request, 'payapp/send_payment.html', {'form': form})

def convert_currency(from_currency, to_currency, amount):
    """Convert amount from one currency to another using the conversion API."""
    # Handle the case where currencies are the same
    if from_currency == to_currency:
        return amount
    
    try:
        # Call our currency conversion API
        response = requests.get(f"http://127.0.0.1:8000/conversion/{from_currency}/{to_currency}/{amount}")
        
        if response.status_code == 200:
            # Extract converted amount from API response
            data = response.json()
            return Decimal(data['converted_amount'])
        else:
            # Fallback to hardcoded conversion rates if API fails
            conversion_rates = {
                'GBP_USD': Decimal('1.30'),
                'GBP_EUR': Decimal('1.17'),
                'USD_GBP': Decimal('0.77'),
                'USD_EUR': Decimal('0.90'),
                'EUR_GBP': Decimal('0.85'),
                'EUR_USD': Decimal('1.11')
            }
            
            rate_key = f"{from_currency}_{to_currency}"
            if rate_key in conversion_rates:
                return amount * conversion_rates[rate_key]
            
            # If no conversion rate is found, return original amount
            return amount
    
    except Exception as e:
        # Log the error (in a production system)
        print(f"Currency conversion error: {e}")
        
        # Use hardcoded rates as fallback
        conversion_rates = {
            'GBP_USD': Decimal('1.30'),
            'GBP_EUR': Decimal('1.17'),
            'USD_GBP': Decimal('0.77'),
            'USD_EUR': Decimal('0.90'),
            'EUR_GBP': Decimal('0.85'),
            'EUR_USD': Decimal('1.11')
        }
        
        rate_key = f"{from_currency}_{to_currency}"
        if rate_key in conversion_rates:
            return amount * conversion_rates[rate_key]
        
        # If no conversion rate is found, return original amount
        return amount

@login_required
def request_payment_view(request):
    if request.method == "POST":
        form = RequestForm(request.POST)
        if form.is_valid():
            sender_email = form.cleaned_data.get('sender_email')
            amount = form.cleaned_data.get('amount')
            
            try:
                # Verify sender exists
                sender = User.objects.get(email=sender_email)
                
                # Prevent requesting from yourself
                if sender == request.user:
                    messages.error(request, "You cannot request money from yourself.")
                    return render(request, 'payapp/request_payment.html', {'form': form})
                
                # Create the pending transaction
                with transaction.atomic():
                    # Create transaction
                    transaction_obj = Transaction.objects.create(
                        sender=sender,
                        receiver=request.user,
                        amount=amount,
                        sender_currency=sender.account.currency,
                        receiver_currency=request.user.account.currency,
                        transaction_type='REQUEST',
                        status='PENDING'
                    )
                    
                    # Log transaction details
                    debug_transaction(transaction_obj, "Payment Requested")
                    
                    # Create notification for sender
                    Notification.objects.create(
                        user=sender,
                        transaction=transaction_obj,
                        is_read=False
                    )
                    
                    # Create notification for requester as well
                    Notification.objects.create(
                        user=request.user,
                        transaction=transaction_obj,
                        is_read=False
                    )
                
                messages.success(request, f"Successfully requested {amount} {request.user.account.currency} from {sender_email}.")
                return redirect('dashboard')
                
            except User.DoesNotExist:
                messages.error(request, "User with this email does not exist.")
    else:
        form = RequestForm()
    
    return render(request, 'payapp/request_payment.html', {'form': form})

@login_required
def notifications_view(request):
    # Get all notifications for the user
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-timestamp')
    
    # Mark all as read
    if request.method == "POST" and 'mark_all_read' in request.POST:
        with transaction.atomic():
            unread_notifications = notifications.filter(is_read=False)
            for notification in unread_notifications:
                notification.is_read = True
                notification.save()
            messages.success(request, "All notifications marked as read.")
            return redirect('notifications')
    
    # Count unread notifications
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count
    }
    
    return render(request, 'payapp/notifications.html', context)

@login_required
def transactions_view(request):
    transaction_type = request.GET.get('type')
    status = request.GET.get('status')
    search_query = request.GET.get('search', '')
    
    # Basic filtering: transactions involving the current user
    transactions = Transaction.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by('-timestamp')
    
    # Apply transaction type filter
    if transaction_type:
        if transaction_type.upper() == 'PAYMENT':
            transactions = transactions.filter(transaction_type='PAYMENT')
        elif transaction_type.upper() == 'REQUEST':
            transactions = transactions.filter(transaction_type='REQUEST')
    
    # Apply status filter
    if status:
        transactions = transactions.filter(status__iexact=status)
    
    # Apply search filter (by sender or recipient email)
    if search_query:
        transactions = transactions.filter(
            Q(sender__email__icontains=search_query) | 
            Q(receiver__email__icontains=search_query) |
            Q(amount__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(transactions, 10)  # 10 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'transactions': page_obj,
        'transaction_type': transaction_type,
        'status': status,
        'search_query': search_query
    }
    
    return render(request, 'payapp/transactions.html', context)

@login_required
def handle_request_view(request, transaction_id, action):
    # Get the transaction
    try:
        transaction = Transaction.objects.get(id=transaction_id)
    except Transaction.DoesNotExist:
        messages.error(request, "Transaction not found.")
        return redirect('notifications')
    
    # Check if this request is meant for this user
    if transaction.sender != request.user:
        messages.error(request, "You don't have permission to handle this request.")
        return redirect('notifications')
    
    # Check if the transaction is still pending
    if transaction.status != 'PENDING':
        messages.error(request, "This request has already been handled.")
        return redirect('notifications')
    
    if action == 'accept':
        # Check if the sender has enough money
        if request.user.account.balance < transaction.amount:
            messages.error(request, "You don't have enough funds to accept this request.")
            return redirect('notifications')
        
        from django.db import transaction as db_transaction
        with db_transaction.atomic():
            # Update transaction status
            transaction.status = 'COMPLETED'
            
            # Calculate converted amount if currencies are different
            sender_account = request.user.account
            receiver_account = transaction.receiver.account
            converted_amount = transaction.amount
            
            if sender_account.currency != receiver_account.currency:
                # Convert the currency
                converted_amount = convert_currency(
                    sender_account.currency,
                    receiver_account.currency,
                    transaction.amount
                )
                # Store the converted amount
                transaction.converted_amount = converted_amount
            
            transaction.save()
            
            # Log transaction details
            debug_transaction(transaction, "Request Accepted")
            
            # Update sender's balance
            sender_account.balance -= transaction.amount
            sender_account.save()
            
            # Update receiver's balance
            receiver_account.balance += converted_amount
            receiver_account.save()
            
            # Create notifications
            Notification.objects.create(
                user=transaction.sender,
                transaction=transaction,
                message=f"You accepted the payment request from {transaction.receiver.email}",
                is_read=False
            )
            
            Notification.objects.create(
                user=transaction.receiver,
                transaction=transaction,
                message=f"{transaction.sender.email} accepted your payment request",
                is_read=False
            )
        
        messages.success(request, "Payment request accepted successfully.")
    
    elif action == 'reject':
        from django.db import transaction as db_transaction
        with db_transaction.atomic():
            # Update transaction status
            transaction.status = 'REJECTED'
            transaction.save()
            
            # Log transaction details
            debug_transaction(transaction, "Request Rejected")
            
            # Create notifications
            Notification.objects.create(
                user=transaction.sender,
                transaction=transaction,
                message=f"You rejected the payment request from {transaction.receiver.email}",
                is_read=False
            )
            
            Notification.objects.create(
                user=transaction.receiver,
                transaction=transaction,
                message=f"{transaction.sender.email} rejected your payment request",
                is_read=False
            )
        
        messages.success(request, "Payment request rejected.")
    
    return redirect('notifications')

@login_required
def admin_dashboard_view(request):
    # Check if user is admin
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')
    
    # Get all user accounts
    accounts = Account.objects.all()
    
    context = {
        'accounts': accounts,
        'user_count': User.objects.count(),
        'transaction_count': Transaction.objects.count()
    }
    
    return render(request, 'payapp/admin_dashboard.html', context)

@login_required
def admin_transactions_view(request):
    # Check if user is admin
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')
    
    # Get all transactions
    transactions = Transaction.objects.all().order_by('-timestamp')
    
    context = {
        'transactions': transactions
    }
    
    return render(request, 'payapp/admin_transactions.html', context)

def transaction_list(request):
    """View to display transaction history with filtering options"""
    # Get the transactions involving the current user
    user = request.user
    transactions = Transaction.objects.filter(
        Q(sender=user) | Q(recipient=user)
    ).select_related('sender', 'recipient').order_by('-timestamp')
    
    # Apply transaction type filter
    transaction_type = request.GET.get('type')
    if transaction_type == 'sent':
        transactions = transactions.filter(sender=user)
    elif transaction_type == 'received':
        transactions = transactions.filter(recipient=user)
    
    # Apply status filter
    status = request.GET.get('status')
    if status:
        transactions = transactions.filter(status=status)
    
    # Apply search filter (by sender or recipient email)
    search_query = request.GET.get('search')
    if search_query:
        transactions = transactions.filter(
            Q(sender__email__icontains=search_query) | 
            Q(recipient__email__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(transactions, 10)  # 10 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'transactions': page_obj,
        'transaction_type': transaction_type,
        'status': status,
        'search_query': search_query
    }
    
    return render(request, 'payapp/transactions.html', context) 