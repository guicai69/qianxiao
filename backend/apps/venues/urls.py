from rest_framework.routers import DefaultRouter
from .views import VenueViewSet, CourtViewSet, TimeSlotViewSet

router = DefaultRouter()
router.register(r'venues', VenueViewSet, basename='venue')
router.register(r'courts', CourtViewSet, basename='court')
router.register(r'time-slots', TimeSlotViewSet, basename='time-slot')
urlpatterns = router.urls
