from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'court', 'date', 'time_slot', 'status', 'amount', 'created_at']
    list_filter = ['status', 'date']
    search_fields = ['user__phone', 'user__nickname', 'court__name']
    date_hierarchy = 'date'
