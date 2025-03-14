from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Transaction, PaymentRequest

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'amount', 'timestamp', 'status')
    list_filter = ('status', 'timestamp')
    search_fields = ('sender__username', 'receiver__username')
    date_hierarchy = 'timestamp'

@admin.register(PaymentRequest)
class PaymentRequestAdmin(admin.ModelAdmin):
    list_display = ('requester', 'target', 'amount', 'timestamp', 'status')
    list_filter = ('status', 'timestamp')
    search_fields = ('requester__username', 'target__username')
    date_hierarchy = 'timestamp'