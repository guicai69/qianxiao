from rest_framework import serializers
from .models import Booking


class BookingListSerializer(serializers.ModelSerializer):
    court_name = serializers.CharField(source='court.name', read_only=True)
    venue_name = serializers.CharField(source='court.venue.name', read_only=True)
    time_slot_display = serializers.CharField(source='time_slot.display', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'user', 'user_phone', 'user_nickname', 'court', 'court_name',
                  'venue_name', 'date', 'time_slot', 'time_slot_display',
                  'amount', 'original_amount', 'discount_rate', 'status',
                  'checked_in', 'checked_in_at', 'created_at']


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
    class Meta:
        model = Booking
        fields = ['court', 'date', 'time_slot']

    def validate(self, attrs):
        court = attrs['court']
        date = attrs['date']
        time_slot = attrs['time_slot']

        if Booking.objects.filter(
            court=court, date=date, time_slot=time_slot,
            status__in=['pending', 'paid'],
        ).exists():
            raise serializers.ValidationError('该时段已被预约，请选择其他时段')

        from datetime import date as d
        if date < d.today():
            raise serializers.ValidationError('不可预约过去的日期')

        if not court.is_active:
            raise serializers.ValidationError('该场地已停用')
        if not time_slot.is_active:
            raise serializers.ValidationError('该时段已停用')

        return attrs


class BookingUpdateStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['cancelled', 'paid'])
    note = serializers.CharField(required=False, allow_blank=True)
