from rest_framework import serializers

from .models import Coupon, UserCoupon


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'name', 'amount', 'min_amount', 'total', 'claimed',
                  'expires_at', 'is_active', 'created_at']


class UserCouponSerializer(serializers.ModelSerializer):
    coupon_name = serializers.CharField(source='coupon.name', read_only=True, default=None)

    class Meta:
        model = UserCoupon
        fields = ['id', 'coupon', 'coupon_name', 'amount', 'min_amount',
                  'expires_at', 'status', 'claimed_at', 'used_at']
