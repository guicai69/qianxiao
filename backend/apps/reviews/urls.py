from rest_framework.routers import DefaultRouter

from .views import ReviewViewSet, FavoriteViewSet, FeedbackViewSet

router = DefaultRouter()
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'feedbacks', FeedbackViewSet, basename='feedback')
urlpatterns = router.urls
