from rest_framework.routers import DefaultRouter
from .views import BookingViewSet, CancellationRequestViewSet

router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'cancellation-requests', CancellationRequestViewSet, basename='cancellation-request')
urlpatterns = router.urls
