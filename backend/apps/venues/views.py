from datetime import date, timedelta

from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.throttling import ScopedRateThrottle
from django.db.models import Count, ProtectedError
from django.db import IntegrityError

from .models import Venue, Court, TimeSlot
from apps.bookings.models import Booking
from apps.bookings.utils import PENDING_TIMEOUT_MINUTES
from apps.common.cache import cache_or_compute
from .serializers import (
    VenueListSerializer, VenuePublicSerializer, VenueDetailSerializer,
    VenueCreateSerializer, VenueUpdateSerializer,
    CourtListSerializer, CourtDetailSerializer, CourtCreateSerializer, CourtUpdateSerializer,
    TimeSlotListSerializer, TimeSlotDetailSerializer, TimeSlotCreateSerializer, TimeSlotUpdateSerializer,
)
from apps.users.permissions import IsAdminOrReception


def parse_int_param(value, name):
    if value in (None, ''):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValidationError({name: f'{name} 参数必须是数字'})


def parse_bool_param(value, name):
    if value in (None, ''):
        return None
    if str(value).lower() in ('true', '1'):
        return True
    if str(value).lower() in ('false', '0'):
        return False
    raise ValidationError({name: f'{name} 参数必须是 true/false'})


class ProtectedDeleteMixin:
    """有预约订单关联的资源不可删除：把 PROTECT 外键的 ProtectedError 转成 400。"""

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response({'detail': '存在关联的预约订单，无法删除'}, status=400)


class IntegrityErrorCreateMixin:
    """预校验与并发写入之间的竞态兜底：唯一约束撞库返回 400 而不是 500。"""

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            return Response({'detail': '数据已存在，请勿重复提交'}, status=400)


class VenueScopedMixin:
    """courts/time-slots 共用：按 venue 过滤 + 读写权限边界。"""

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAdminOrReception()]

    def get_queryset(self):
        qs = super().get_queryset()
        venue_id = parse_int_param(self.request.query_params.get('venue'), 'venue')
        if venue_id:
            qs = qs.filter(venue_id=venue_id)
        return qs


class VenueViewSet(ProtectedDeleteMixin, IntegrityErrorCreateMixin, viewsets.ModelViewSet):
    queryset = Venue.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        name = self.request.query_params.get('name')
        is_active = parse_bool_param(self.request.query_params.get('is_active'), 'is_active')
        if name:
            qs = qs.filter(name__icontains=name)
        if is_active is not None:
            qs = qs.filter(is_active=is_active)
        # 列表页只查一次 court_count，避免 count() 逐条打库（N+1）
        if self.action == 'list':
            qs = qs.annotate(court_count=Count('courts'))
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return VenueListSerializer
        if self.action == 'create':
            return VenueCreateSerializer
        if self.action in ('update', 'partial_update'):
            return VenueUpdateSerializer
        return VenueDetailSerializer

    def get_permissions(self):
        # 注意：本类的 get_permissions() 会覆盖 @action(permission_classes=...)，
        # 新开的动作必须在这里登记，否则会掉进最后那条 IsAdminOrReception
        if self.action == 'public':
            return [AllowAny()]
        if self.action in ('list', 'retrieve', 'availability'):
            return [IsAuthenticated()]
        return [IsAdminOrReception()]

    @action(detail=False, methods=['get'], authentication_classes=[],
            throttle_classes=[ScopedRateThrottle])
    def public(self, request):
        """游客可见的场馆清单（给未登录的首页用）。

        只读，只返回场馆基础信息，不含场地、时段与价格明细，也不含联系电话。
        单独开一个动作而不是放宽 list/retrieve 的权限，是为了保住
        "登录后才能查可预约时段"这条边界。权限在 get_permissions() 里登记。
        """
        self.throttle_scope = 'venue-public'

        def compute():
            qs = (Venue.objects.filter(is_active=True)
                  .annotate(court_count=Count('courts')).order_by('id'))
            return VenuePublicSerializer(qs, many=True).data

        # 场馆只有个位数，整单缓存 5 分钟；分页在缓存后的列表上做
        data = cache_or_compute('venue-public-all', 300, compute)
        page = self.paginate_queryset(data)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(data)

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """返回指定日期被占用的时段（仅 court_id + time_slot_id，不含用户信息）"""
        venue = self.get_object()
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({'detail': '缺少 date 参数'}, status=400)
        try:
            bdate = date.fromisoformat(date_str)
        except ValueError:
            return Response({'detail': 'date 参数格式错误'}, status=400)

        # 纯读接口：GET 不写库。超过支付时限仍未支付的订单在这里「视为已释放」，
        # 真正落库取消交给定时任务 cancel_expired_bookings / 下单时的惰性清理。
        # 占用列表缓存 30 秒，下单/支付/取消时主动失效
        def compute():
            # 只返回「页面上真能看到」的占用：停用场地/停用时段的历史订单一律剔除，
            # 否则前端的「当天还剩几个可约格」会被这些看不见的格子算少
            overdue = timezone.now() - timedelta(minutes=PENDING_TIMEOUT_MINUTES)
            qs = Booking.objects.filter(
                court__venue=venue, court__is_active=True,
                time_slot__is_active=True, date=bdate,
            ).exclude(status='cancelled').exclude(status='pending', created_at__lt=overdue)
            return [
                {'court_id': b.court_id, 'time_slot_id': b.time_slot_id}
                for b in qs
            ]

        occupied = cache_or_compute(f'availability:{venue.id}:{date_str}', 30, compute)
        return Response({'date': date_str, 'occupied': occupied})


class CourtViewSet(VenueScopedMixin, ProtectedDeleteMixin, IntegrityErrorCreateMixin, viewsets.ModelViewSet):
    queryset = Court.objects.select_related('venue').all()

    def get_serializer_class(self):
        if self.action == 'list':
            return CourtListSerializer
        if self.action == 'create':
            return CourtCreateSerializer
        if self.action in ('update', 'partial_update'):
            return CourtUpdateSerializer
        return CourtDetailSerializer


class TimeSlotViewSet(VenueScopedMixin, ProtectedDeleteMixin, IntegrityErrorCreateMixin, viewsets.ModelViewSet):
    queryset = TimeSlot.objects.select_related('venue').all()

    def get_serializer_class(self):
        if self.action == 'list':
            return TimeSlotListSerializer
        if self.action == 'create':
            return TimeSlotCreateSerializer
        if self.action in ('update', 'partial_update'):
            return TimeSlotUpdateSerializer
        return TimeSlotDetailSerializer
