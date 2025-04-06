from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import UserProfile
from payapp.models import Account
from decimal import Decimal

def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Create user
                user = form.save()
                # Get user's selected currency
                currency = form.cleaned_data.get('currency')
                # Create user profile
                profile = UserProfile.objects.create(
                    user=user,
                    currency=currency
                )
                
                # Set initial balance (£750 or equivalent in selected currency)
                initial_amount = Decimal('750.00')
                
                # Convert initial amount based on selected currency
                if currency == 'USD':
                    initial_amount = initial_amount * Decimal('1.30')  # Example exchange rate
                elif currency == 'EUR':
                    initial_amount = initial_amount * Decimal('1.17')  # Example exchange rate
                
                # Create account
                Account.objects.create(
                    user=user,
                    balance=initial_amount,
                    currency=currency
                )
                
                # Auto login
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=user.username, password=raw_password)
                login(request, user)
                messages.success(request, f"Account created successfully! Initial balance: {initial_amount} {currency}")
                return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register/register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid username or password")
    else:
        form = AuthenticationForm()
    
    return render(request, 'register/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "Successfully logged out")
    return redirect('login')

@login_required
def register_admin_view(request):
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page")
        return redirect('dashboard')
    
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Create user
                user = form.save()
                # Get selected currency
                currency = form.cleaned_data.get('currency')
                # Create user profile
                profile = UserProfile.objects.create(
                    user=user,
                    currency=currency
                )
                
                # Set initial balance
                initial_amount = Decimal('750.00')
                
                # Convert initial amount based on selected currency
                if currency == 'USD':
                    initial_amount = initial_amount * Decimal('1.30')
                elif currency == 'EUR':
                    initial_amount = initial_amount * Decimal('1.17')
                
                # Create account
                Account.objects.create(
                    user=user,
                    balance=initial_amount,
                    currency=currency
                )
                
                # Set as admin
                user.is_staff = True
                user.save()
                
                messages.success(request, f"Admin account {user.username} created successfully!")
                return redirect('admin_dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register/register_admin.html', {'form': form}) 