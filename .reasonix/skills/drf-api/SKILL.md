---
name: drf-api
description: DRF Serializer + ViewSet + Router 标准写法模板 — 本项目 API 层规范
---

# drf-api — DRF Serializer + ViewSet 标准模板

本项目使用 Django REST Framework，API 层遵循以下约定。

## 目录结构（每个 app 内）

```
apps/<app_name>/
├── models.py          # Model
├── serializers.py     # Serializer（输入/输出分离）
├── views.py           # ViewSet
├── urls.py            # Router 注册
└── permissions.py     # 自定义权限（按需）
```

## Serializer 模板

每个 Model 至少有 3 个 Serializer：

```python
from rest_framework import serializers
from .models import Booking

# 1. 列表用（精简字段）
class BookingListSerializer(serializers.ModelSerializer):
    court_name = serializers.CharField(source='court.name', read_only=True)
    time_slot_display = serializers.CharField(source='time_slot.display', read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'court_name', 'date', 'time_slot_display', 'status', 'amount', 'created_at']

# 2. 详情用（全字段 + 嵌套）
class BookingDetailSerializer(serializers.ModelSerializer):
    court = CourtSimpleSerializer(read_only=True)
    user = UserSimpleSerializer(read_only=True)
    time_slot = TimeSlotSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'

# 3. 创建/更新用（校验逻辑）
class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['court', 'date', 'time_slot']

    def validate(self, attrs):
        """冲突检测：同一场地同一时段不可重复预约"""
        if Booking.objects.filter(
            court=attrs['court'],
            date=attrs['date'],
            time_slot=attrs['time_slot'],
            status__in=['pending', 'paid'],
        ).exists():
            raise serializers.ValidationError("该时段已被预约")
        return attrs
```

## ViewSet 模板

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Booking
from .serializers import (
    BookingListSerializer,
    BookingDetailSerializer,
    BookingCreateSerializer,
)
from .permissions import IsAdminOrReception, IsOwnerOrStaff

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.select_related('user', 'court', 'time_slot').all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return BookingListSerializer
        if self.action == 'create':
            return BookingCreateSerializer
        return BookingDetailSerializer

    def get_queryset(self):
        """会员只看自己的订单，管理员/前台看全部"""
        qs = super().get_queryset()
        if self.request.user.role == 'member':
            return qs.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消预约"""
        booking = self.get_object()
        if booking.status != 'pending':
            return Response({'error': '只有待支付订单可取消'}, status=400)
        booking.status = 'cancelled'
        booking.save()
        return Response({'status': 'cancelled'})
```

## Router 注册

```python
# apps/bookings/urls.py
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet

router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')
urlpatterns = router.urls
```

## 分页配置

```python
# config/settings/base.py
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}
```

## 自定义权限模板

```python
from rest_framework.permissions import BasePermission

class IsOwnerOrStaff(BasePermission):
    """本人 或 管理员/前台 可操作"""
    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'reception']:
            return True
        return obj.user == request.user
```

## 统一响应格式

```python
# 成功
Response({'code': 200, 'data': serializer.data, 'message': 'ok'})

# 失败
Response({'code': 400, 'data': None, 'message': '该时段已被预约'}, status=400)
```

## API 命名约定

| 操作 | HTTP 方法 | URL |
|------|-----------|-----|
| 列表 | GET | `/api/bookings/` |
| 详情 | GET | `/api/bookings/{id}/` |
| 创建 | POST | `/api/bookings/` |
| 更新 | PUT/PATCH | `/api/bookings/{id}/` |
| 删除 | DELETE | `/api/bookings/{id}/` |
| 自定义 | POST | `/api/bookings/{id}/cancel/` |
