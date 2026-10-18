from django.utils import timezone
from rest_framework import serializers

from .models import Coupon, UserCoupon


class CouponSerializer(serializers.ModelSerializer):
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = ['id', 'name', 'amount', 'min_amount', 'total', 'claimed',
                  'expires_at', 'is_active', 'is_expired', 'created_at']

    def get_is_expired(self, obj):
        return obj.expires_at <= timezone.now()


class UserCouponSerializer(serializers.ModelSerializer):
    coupon_name = serializers.CharField(source='coupon.name', read_only=True, default=None)
    expiry_status = serializers.SerializerMethodField()

    class Meta:
        model = UserCoupon
        fields = ['id', 'coupon', 'coupon_name', 'amount', 'min_amount',
                  'expires_at', 'status', 'expiry_status', 'claimed_at', 'used_at']

    def get_expiry_status(self, obj):
        if obj.status == UserCoupon.STATUS_USED:
            return 'used'
        if obj.expires_at <= timezone.now():
            return 'expired'
        return 'unused'
