from django.urls import path
from . import views

app_name = 'payapp'

urlpatterns = [
    path('', views.home, name='home'),
    path('transactions/', views.transactions, name='transactions'),
    path('pay/', views.make_payment, name='pay'),
    path('request/', views.request_payment, name='request'),
    path('transaction-history/', views.transaction_history, name='transaction_history'),
]