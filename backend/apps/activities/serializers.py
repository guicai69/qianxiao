from rest_framework import serializers

from .models import Activity, Registration


class ActivitySerializer(serializers.ModelSerializer):
    venue_name = serializers.CharField(source='venue.name', read_only=True)
    my_registration = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = ['id', 'venue', 'venue_name', 'type', 'title', 'description',
                  'start_at', 'end_at', 'price', 'capacity', 'registered',
                  'deadline', 'is_active', 'my_registration', 'created_at']

    def get_my_registration(self, obj):
        regs = getattr(obj, 'my_regs', None)
        if not regs:
            return None
        return RegistrationSerializer(regs[0]).data

    def validate(self, attrs):
        start = attrs.get('start_at', getattr(self.instance, 'start_at', None))
        end = attrs.get('end_at', getattr(self.instance, 'end_at', None))
        deadline = attrs.get('deadline', getattr(self.instance, 'deadline', None))
        if start and end and start >= end:
            raise serializers.ValidationError('结束时间必须大于开始时间')
        if start and deadline and deadline > start:
            raise serializers.ValidationError('报名截止不能晚于开始时间')
        return attrs


class RegistrationSerializer(serializers.ModelSerializer):
    activity_title = serializers.CharField(source='activity.title', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)

    class Meta:
        model = Registration
        fields = ['id', 'activity', 'activity_title', 'user', 'user_phone', 'user_nickname',
                  'price', 'status', 'created_at']
