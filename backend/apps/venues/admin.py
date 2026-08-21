from django.contrib import admin
from .models import Venue, Court, TimeSlot


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'address', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'address', 'phone']
    ordering = ['-created_at']


@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'venue', 'is_active', 'created_at']
    list_filter = ['venue', 'is_active']
    search_fields = ['name']


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['id', 'venue', 'start_time', 'end_time', 'display', 'price', 'is_active']
    list_filter = ['venue', 'is_active']
    search_fields = ['venue__name']
