from decimal import Decimal
from rest_framework import serializers
from .models import Payment


class PaymentListSerializer(serializers.ModelSerializer):
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    booking_date = serializers.CharField(source='booking.date', read_only=True, default=None)
    booking_court = serializers.CharField(source='booking.court.name', read_only=True, default=None)
    booking_time = serializers.CharField(source='booking.time_slot.display', read_only=True, default=None)

    class Meta:
        model = Payment
        fields = ['id', 'user', 'user_phone', 'user_nickname', 'booking', 'booking_date',
                  'booking_court', 'booking_time', 'type', 'amount', 'bonus', 'method',
                  'status', 'created_at']


class PaymentDetailSerializer(serializers.ModelSerializer):
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'


class RechargeSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    method = serializers.ChoiceField(
        choices=[('wechat', '微信'), ('alipay', '支付宝')],
        default='wechat',
    )


class PayBookingSerializer(serializers.Serializer):
    booking_id = serializers.IntegerField()
    method = serializers.ChoiceField(
        choices=[('balance', '余额支付'), ('wechat', '微信支付'), ('alipay', '支付宝')],
        default='balance',
    )
