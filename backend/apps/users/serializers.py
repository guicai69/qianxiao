from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from .models import User
from apps.common.captcha import verify as verify_captcha


class RegisterSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(
        max_length=11,
        validators=[RegexValidator(r'^1\d{10}$', '请输入正确的手机号')],
    )
    password = serializers.CharField(
        write_only=True, min_length=6,
        validators=[validate_password],
        label='密码',
    )
    password2 = serializers.CharField(write_only=True, label='确认密码')
    captcha_id = serializers.CharField(write_only=True, required=False, allow_blank=True)
    captcha_code = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['phone', 'password', 'password2', 'nickname', 'captcha_id', 'captcha_code']

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError('该手机号已注册')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password2': '两次密码不一致'})
        if not verify_captcha(attrs.get('captcha_id'), attrs.get('captcha_code')):
            raise serializers.ValidationError({'captcha_code': '验证码错误或已过期'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        validated_data.pop('captcha_id', None)
        validated_data.pop('captcha_code', None)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField(label='手机号')
    password = serializers.CharField(label='密码', write_only=True)
    captcha_id = serializers.CharField(write_only=True, required=False, allow_blank=True)
    captcha_code = serializers.CharField(write_only=True, required=False, allow_blank=True)

    def validate(self, attrs):
        phone = attrs.get('phone')
        password = attrs.get('password')
        if not verify_captcha(attrs.get('captcha_id'), attrs.get('captcha_code')):
            raise serializers.ValidationError({'captcha_code': '验证码错误或已过期'})
        user = authenticate(request=self.context.get('request'), username=phone, password=password)
        if not user:
            raise serializers.ValidationError('手机号或密码错误')
        if not user.is_active:
            raise serializers.ValidationError('该账号已被禁用')
        attrs['user'] = user
        return attrs


class UserInfoSerializer(serializers.ModelSerializer):
    """个人 / 列表信息"""
    discount_rate = serializers.SerializerMethodField()
    total_spend = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'phone', 'nickname', 'role', 'level', 'balance',
                  'discount_rate', 'total_spend', 'date_joined', 'last_login', 'is_active']

    def get_discount_rate(self, obj):
        return str(obj.get_discount_rate())

    def get_total_spend(self, obj):
        return str(obj.get_total_spend())


class UserUpdateSerializer(serializers.ModelSerializer):
    """修改个人信息（昵称）"""

    class Meta:
        model = User
        fields = ['nickname']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, label='旧密码')
    new_password = serializers.CharField(
        write_only=True, min_length=6, validators=[validate_password],
        label='新密码',
    )
    new_password2 = serializers.CharField(write_only=True, label='确认新密码')

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('旧密码不正确')
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({'new_password2': '两次密码不一致'})
        return attrs

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class AdminUserCreateSerializer(serializers.ModelSerializer):
    """管理员创建用户（可指定角色）"""
    password = serializers.CharField(write_only=True, min_length=6, label='密码')

    class Meta:
        model = User
        fields = ['phone', 'password', 'nickname', 'role', 'level']

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError('该手机号已存在')
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """管理员修改用户（角色/等级/状态）"""

    class Meta:
        model = User
        fields = ['nickname', 'role', 'level', 'is_active', 'is_blacklisted']
