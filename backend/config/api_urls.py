"""API URL aggregator — includes all app routers."""
from django.urls import path, include

urlpatterns = [
    path('', include('apps.users.urls')),
    path('', include('apps.venues.urls')),
    path('', include('apps.bookings.urls')),
    path('', include('apps.payments.urls')),
    path('', include('apps.stats.urls')),
    path('', include('apps.announcements.urls')),
]
