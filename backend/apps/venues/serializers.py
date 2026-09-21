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
        # 列表视图用 annotate 一次性取数，避免逐条 count() 打库（N+1）
        if hasattr(obj, 'court_count'):
            return obj.court_count
        return obj.courts.count()


class VenuePublicSerializer(VenueListSerializer):
    """游客接口专用：不暴露联系电话。"""

    class Meta(VenueListSerializer.Meta):
        fields = ['id', 'name', 'address', 'is_active', 'court_count', 'created_at', 'updated_at']


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

    def validate_name(self, value):
        qs = Venue.objects.filter(name=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('该场馆名称已存在')
        return value


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

    def validate(self, attrs):
        if Court.objects.filter(venue=attrs['venue'], name=attrs['name']).exists():
            raise serializers.ValidationError('该场馆下已存在同名场地')
        return attrs


class CourtUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Court
        fields = ['name', 'is_active']

    def validate(self, attrs):
        name = attrs.get('name', getattr(self.instance, 'name', None))
        venue = getattr(self.instance, 'venue', None)
        if name and venue and Court.objects.filter(venue=venue, name=name).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError('该场馆下已存在同名场地')
        return attrs


# ──────────────────────────────────────────────
# TimeSlot Serializers
# ──────────────────────────────────────────────
class DiscountedPriceMixin:
    """三个时段序列化器共用：按当前用户折扣率算折后价。"""

    def get_discounted_price(self, obj):
        request = self.context.get('request')
        if request and getattr(request, 'user', None) and request.user.is_authenticated:
            return (obj.price * request.user.get_discount_rate()).quantize(Decimal('0.01'))
        return obj.price


class TimeSlotSimpleSerializer(DiscountedPriceMixin, serializers.ModelSerializer):
    display = serializers.CharField(read_only=True)
    discounted_price = serializers.SerializerMethodField()

    class Meta:
        model = TimeSlot
        fields = ['id', 'start_time', 'end_time', 'price', 'discounted_price',
                  'display', 'is_active']


class TimeSlotListSerializer(DiscountedPriceMixin, serializers.ModelSerializer):
    venue_name = serializers.CharField(source='venue.name', read_only=True)
    display = serializers.CharField(read_only=True)
    discounted_price = serializers.SerializerMethodField()

    class Meta:
        model = TimeSlot
        fields = ['id', 'venue', 'venue_name', 'start_time', 'end_time',
                  'display', 'price', 'discounted_price', 'is_active',
                  'created_at', 'updated_at']


class TimeSlotDetailSerializer(DiscountedPriceMixin, serializers.ModelSerializer):
    venue = VenueListSerializer(read_only=True)
    display = serializers.CharField(read_only=True)
    discounted_price = serializers.SerializerMethodField()

    class Meta:
        model = TimeSlot
        fields = ['id', 'venue', 'start_time', 'end_time', 'price',
                  'discounted_price', 'display', 'is_active', 'created_at', 'updated_at']


class TimeSlotCreateSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0'))

    class Meta:
        model = TimeSlot
        fields = ['id', 'venue', 'start_time', 'end_time', 'price', 'is_active']

    def validate(self, attrs):
        check_slot_conflict(attrs['venue'], attrs['start_time'], attrs['end_time'], None)
        return attrs


def check_slot_conflict(venue, start, end, exclude_pk):
    if start >= end:
        raise serializers.ValidationError('结束时间必须大于开始时间')
    qs = TimeSlot.objects.filter(venue=venue)
    if exclude_pk is not None:
        qs = qs.exclude(pk=exclude_pk)
    if qs.filter(start_time=start, end_time=end).exists():
        raise serializers.ValidationError('该时段已存在')
    if qs.filter(start_time__lt=end, end_time__gt=start).exists():
        raise serializers.ValidationError('时段与现有时段重叠，请调整起止时间')


class TimeSlotUpdateSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0'))

    class Meta:
        model = TimeSlot
        fields = ['start_time', 'end_time', 'price', 'is_active']

    def validate(self, attrs):
        # 部分更新时用实例上的旧值补齐，避免只改 start/end 一端绕过校验
        venue = getattr(self.instance, 'venue', None)
        start = attrs.get('start_time', getattr(self.instance, 'start_time', None))
        end = attrs.get('end_time', getattr(self.instance, 'end_time', None))
        if venue and start and end:
            check_slot_conflict(venue, start, end, self.instance.pk)
        return attrs
