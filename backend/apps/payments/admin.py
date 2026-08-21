from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'type', 'amount', 'method', 'status', 'booking', 'created_at']
    list_filter = ['type', 'method', 'status']
    search_fields = ['user__phone', 'user__nickname']
    date_hierarchy = 'created_at'
