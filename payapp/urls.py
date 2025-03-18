from django.urls import path
from . import views
from . import api

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('send-payment/', views.send_payment_view, name='send_payment'),
    path('request-payment/', views.request_payment_view, name='request_payment'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('transactions/', views.transactions_view, name='transactions'),
    path('handle-request/<int:transaction_id>/<str:action>/', views.handle_request_view, name='handle_request'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-transactions/', views.admin_transactions_view, name='admin_transactions'),
    path('conversion/<str:currency1>/<str:currency2>/<str:amount>/', api.conversion_view, name='conversion'),
] 