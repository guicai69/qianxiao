from rest_framework import serializers
from .models import Booking, CancellationRequest


class BookingListSerializer(serializers.ModelSerializer):
    court_name = serializers.CharField(source='court.name', read_only=True)
    venue_name = serializers.CharField(source='court.venue.name', read_only=True)
    time_slot_display = serializers.CharField(source='time_slot.display', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    cancellation_status = serializers.SerializerMethodField()
    cancel_window = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ['id', 'user', 'user_phone', 'user_nickname', 'court', 'court_name',
                  'venue_name', 'date', 'time_slot', 'time_slot_display',
                  'amount', 'original_amount', 'discount_rate', 'coupon_amount', 'status',
                  'checked_in', 'checked_in_at', 'created_at',
                  'cancellation_status', 'cancel_window']

    def get_cancellation_status(self, obj):
        req = obj.cancellation_requests.order_by('-created_at').first()
        return req.status if req else None

    def get_cancel_window(self, obj):
        """free=开场前2小时外可直取消；request=2小时内需申请退场；started=已开场"""
        if obj.status != 'paid':
            return None
        from datetime import datetime, timedelta
        from django.utils import timezone
        slot_start = datetime.combine(
            obj.date, obj.time_slot.start_time, tzinfo=timezone.get_current_timezone(),
        )
        now = timezone.now()
        if now >= slot_start:
            return 'started'
        if (slot_start - now) > timedelta(hours=2):
            return 'free'
        return 'request'


class BookingDetailSerializer(serializers.ModelSerializer):
    court_name = serializers.CharField(source='court.name', read_only=True)
    venue_name = serializers.CharField(source='court.venue.name', read_only=True)
    venue_id = serializers.IntegerField(source='court.venue.id', read_only=True)
    time_slot_display = serializers.CharField(source='time_slot.display', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'


class BookingCreateSerializer(serializers.ModelSerializer):
    user_coupon_id = serializers.IntegerField(required=False, write_only=True)

    class Meta:
        model = Booking
        fields = ['court', 'date', 'time_slot', 'user_coupon_id']

    def validate(self, attrs):
        court = attrs['court']
        date = attrs['date']
        time_slot = attrs['time_slot']

        from datetime import date as d
        if date < d.today():
            raise serializers.ValidationError('不可预约过去的日期')

        if court.venue_id != time_slot.venue_id:
            raise serializers.ValidationError('场地与时段不属于同一场馆')
        if not court.is_active:
            raise serializers.ValidationError('该场地已停用')
        if not time_slot.is_active:
            raise serializers.ValidationError('该时段已停用')

        return attrs


class CancellationRequestSerializer(serializers.ModelSerializer):
    booking_date = serializers.DateField(source='booking.date', read_only=True)
    venue_name = serializers.CharField(source='booking.court.venue.name', read_only=True)
    court_name = serializers.CharField(source='booking.court.name', read_only=True)
    time_slot_display = serializers.CharField(source='booking.time_slot.display', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)

    class Meta:
        model = CancellationRequest
        fields = ['id', 'booking', 'booking_date', 'venue_name', 'court_name',
                  'time_slot_display', 'user', 'user_phone', 'user_nickname',
                  'reason', 'refund_amount', 'fee_amount', 'status', 'reject_reason',
                  'reviewed_at', 'refund_at', 'refunded_at', 'created_at']


class CancellationRequestCreateSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, max_length=200)
