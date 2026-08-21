from rest_framework import serializers
from .models import Venue, Court, TimeSlot
from decimal import Decimal


# ──────────────────────────────────────────────
# Venue Serializers
# ──────────────────────────────────────────────
class VenueListSerializer(serializers.ModelSerializer):
    court_count = serializers.SerializerMethodField()

    class Meta:
        model = Venue
        fields = ['id', 'name', 'address', 'phone', 'is_active',
                  'court_count', 'created_at', 'updated_at']

    def get_court_count(self, obj):
        return obj.courts.count()


class VenueDetailSerializer(serializers.ModelSerializer):
    courts = serializers.SerializerMethodField()
    time_slots = serializers.SerializerMethodField()

    class Meta:
        model = Venue
        fields = '__all__'

    def get_courts(self, obj):
        qs = obj.courts.filter(is_active=True)
        return CourtSimpleSerializer(qs, many=True).data

    def get_time_slots(self, obj):
        qs = obj.time_slots.filter(is_active=True)
        return TimeSlotSimpleSerializer(qs, many=True, context=self.context).data


class VenueCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = ['id', 'name', 'address', 'phone', 'description', 'is_active']

    def validate_name(self, value):
        if Venue.objects.filter(name=value).exists():
            raise serializers.ValidationError('该场馆名称已存在')
        return value


class VenueUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = ['name', 'address', 'phone', 'description', 'is_active']


# ──────────────────────────────────────────────
# Court Serializers
# ──────────────────────────────────────────────
class CourtSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Court
        fields = ['id', 'name', 'is_active']


class CourtListSerializer(serializers.ModelSerializer):
    venue_name = serializers.CharField(source='venue.name', read_only=True)

    class Meta:
        model = Court
        fields = ['id', 'venue', 'venue_name', 'name', 'is_active', 'created_at', 'updated_at']


class CourtDetailSerializer(serializers.ModelSerializer):
    venue = VenueListSerializer(read_only=True)

    class Meta:
        model = Court
        fields = '__all__'


class CourtCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Court
        fields = ['id', 'venue', 'name', 'is_active']


class CourtUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Court
        fields = ['name', 'is_active']


# ──────────────────────────────────────────────
# TimeSlot Serializers
# ──────────────────────────────────────────────
class TimeSlotSimpleSerializer(serializers.ModelSerializer):
    display = serializers.CharField(read_only=True)
    discounted_price = serializers.SerializerMethodField()

    class Meta:
        model = TimeSlot
        fields = ['id', 'start_time', 'end_time', 'price', 'discounted_price',
                  'display', 'is_active']

    def get_discounted_price(self, obj):
        request = self.context.get('request')
        if request and getattr(request, 'user', None) and request.user.is_authenticated:
            return (obj.price * request.user.get_discount_rate()).quantize(Decimal('0.01'))
        return obj.price


class TimeSlotListSerializer(serializers.ModelSerializer):
    venue_name = serializers.CharField(source='venue.name', read_only=True)
    display = serializers.CharField(read_only=True)
    discounted_price = serializers.SerializerMethodField()

    class Meta:
        model = TimeSlot
        fields = ['id', 'venue', 'venue_name', 'start_time', 'end_time',
                  'display', 'price', 'discounted_price', 'is_active',
                  'created_at', 'updated_at']

    def get_discounted_price(self, obj):
        request = self.context.get('request')
        if request and getattr(request, 'user', None) and request.user.is_authenticated:
            return (obj.price * request.user.get_discount_rate()).quantize(Decimal('0.01'))
        return obj.price


class TimeSlotDetailSerializer(serializers.ModelSerializer):
    venue = VenueListSerializer(read_only=True)
    display = serializers.CharField(read_only=True)
    discounted_price = serializers.SerializerMethodField()

    class Meta:
        model = TimeSlot
        fields = ['id', 'venue', 'start_time', 'end_time', 'price',
                  'discounted_price', 'display', 'is_active', 'created_at', 'updated_at']

    def get_discounted_price(self, obj):
        request = self.context.get('request')
        if request and getattr(request, 'user', None) and request.user.is_authenticated:
            return (obj.price * request.user.get_discount_rate()).quantize(Decimal('0.01'))
        return obj.price


class TimeSlotCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id', 'venue', 'start_time', 'end_time', 'price', 'is_active']

    def validate(self, attrs):
        if attrs['start_time'] >= attrs['end_time']:
            raise serializers.ValidationError('结束时间必须大于开始时间')
        return attrs


class TimeSlotUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['start_time', 'end_time', 'price', 'is_active']

    def validate(self, attrs):
        if attrs.get('start_time') and attrs.get('end_time') and attrs['start_time'] >= attrs['end_time']:
            raise serializers.ValidationError('结束时间必须大于开始时间')
        return attrs
