from rest_framework import serializers

from .models import Review, Favorite, Feedback


class ReviewSerializer(serializers.ModelSerializer):
    venue_name = serializers.CharField(source='booking.court.venue.name', read_only=True, default=None)
    court_name = serializers.CharField(source='booking.court.name', read_only=True, default=None)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'booking', 'user', 'user_phone', 'user_nickname', 'venue_name',
                  'court_name', 'rating', 'content', 'reply', 'replied_at', 'created_at']
        read_only_fields = ['reply', 'replied_at']


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['booking', 'rating', 'content']


class FavoriteSerializer(serializers.ModelSerializer):
    venue_name = serializers.CharField(source='venue.name', read_only=True)
    venue_address = serializers.CharField(source='venue.address', read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'venue', 'venue_name', 'venue_address', 'created_at']


class FeedbackSerializer(serializers.ModelSerializer):
    user_phone = serializers.CharField(source='user.phone', read_only=True)

    class Meta:
        model = Feedback
        fields = ['id', 'user', 'user_phone', 'content', 'status', 'reply', 'created_at', 'processed_at']
        read_only_fields = ['user', 'status', 'reply', 'processed_at']
