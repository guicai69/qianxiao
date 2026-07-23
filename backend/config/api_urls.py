"""API URL aggregator — includes all app routers."""
from django.urls import path, include

urlpatterns = [
    path('', include('apps.users.urls')),
    # Future apps will register their routes here
]
