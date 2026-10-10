import csv

from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import date, datetime, timedelta
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import F
from django.http import HttpResponse
from django.utils import timezone
from decimal import Decimal

from .models import Booking
from .serializers import (
    BookingListSerializer, BookingDetailSerializer,
    BookingCreateSerializer,
)
from .utils import cancel_expired_pendings, FREE_CANCEL_WINDOW, CANCEL_FEE_RATE
from apps.common.cache import invalidate
from apps.payments.models import Payment
from apps.users.permissions import IsAdminOrReception
from apps.venues.models import Court

User = get_user_model()


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.select_related(
        'user', 'court', 'time_slot', 'court__venue'
    ).all()

    def get_serializer_class(self):
        if self.action == 'list':
            return BookingListSerializer
        if self.action == 'create':
            return BookingCreateSerializer
        return BookingDetailSerializer

    def get_permissions(self):
        if self.action in ('create', 'list', 'my', 'retrieve', 'cancel'):
            return [IsAuthenticated()]
        return [IsAdminOrReception()]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            BookingDetailSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED,
        )

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        # Members see own bookings only
        if user.role == 'member':
            qs = qs.filter(user=user)

        # Hide cancelled bookings older than 2 days
        two_days_ago = date.today() - timedelta(days=2)
        qs = qs.exclude(status='cancelled', date__lt=two_days_ago)

        # Filters（参数先校验再过滤，非法输入返回 400 而不是 500）
        venue = self.request.query_params.get('venue')
        if venue:
            try:
                venue = int(venue)
            except (TypeError, ValueError):
                raise serializers.ValidationError({'venue': 'venue 参数必须是数字'})
            qs = qs.filter(court__venue_id=venue)

        bdate = self.request.query_params.get('date')
        if bdate:
            try:
                bdate = date.fromisoformat(bdate)
            except ValueError:
                raise serializers.ValidationError({'date': 'date 参数格式错误'})
            qs = qs.filter(date=bdate)

        status_filter = self.request.query_params.get('status')
        if status_filter:
            if status_filter not in dict(Booking.STATUS_CHOICES):
                raise serializers.ValidationError({'status': 'status 参数不合法'})
            qs = qs.filter(status=status_filter)

        return qs.order_by('-created_at')

    def perform_create(self, serializer):
        court = serializer.validated_data['court']
        date = serializer.validated_data['date']
        time_slot = serializer.validated_data['time_slot']

        # 惰性取消过期未支付订单，释放被占坑的时段
        cancel_expired_pendings()

        # 锁场地行，串行化同场地的下单，从根上防止同一场地同时段被双写
        Court.objects.select_for_update().get(pk=court.pk)
        if Booking.objects.filter(
            court=court, date=date, time_slot=time_slot,
            status__in=['pending', 'paid'],
        ).exists():
            raise serializers.ValidationError('该时段已被预约，请选择其他时段')

        original_amount = time_slot.price
        discount_rate = self.request.user.get_discount_rate()

        # 优惠券：先满减后会员折扣（金额快照到订单，支付成功时才核销券）
        user_coupon = None
        coupon_amount = Decimal('0')
        user_coupon_id = serializer.validated_data.get('user_coupon_id')
        if user_coupon_id:
            from apps.coupons.models import UserCoupon
            try:
                user_coupon = UserCoupon.objects.select_for_update().get(
                    pk=user_coupon_id, user=self.request.user, status='unused',
                    expires_at__gt=timezone.now(),
                )
            except UserCoupon.DoesNotExist:
                raise serializers.ValidationError('优惠券不存在、已使用或已过期')
            if original_amount < user_coupon.min_amount:
                raise serializers.ValidationError(
                    f'未满 ¥{user_coupon.min_amount}，该优惠券不可用')
            coupon_amount = min(user_coupon.amount, original_amount)
            original_amount -= coupon_amount

        amount = (original_amount * discount_rate).quantize(Decimal('0.01'))
        serializer.save(
            user=self.request.user,
            amount=amount,
            original_amount=time_slot.price,
            discount_rate=discount_rate,
            user_coupon=user_coupon,
            coupon_amount=coupon_amount,
        )
        invalidate(f'availability:{court.venue_id}:{date.isoformat()}')

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def cancel(self, request, pk=None):
        # get_object() 只做归属校验（会员只能取消自己的订单）
        booking_id = self.get_object().pk
        is_staff = request.user.role in ('admin', 'reception')

        # 行锁内重读后再做状态判断与退款计算，防止并发取消双退款
        booking = Booking.objects.select_for_update().select_related('user').get(pk=booking_id)
        if booking.status == 'cancelled':
            return Response({'detail': '该订单已取消'}, status=400)
        if booking.status not in ['pending', 'paid']:
            return Response({'detail': '该订单状态不可取消'}, status=400)

        was_paid = booking.status == 'paid'
        user = booking.user
        refund_amount = Decimal('0')
        fee_amount = Decimal('0')

        if was_paid:
            slot_start = datetime.combine(
                booking.date, booking.time_slot.start_time,
                tzinfo=timezone.get_current_timezone(),
            )
            now = timezone.now()
            if now >= slot_start:
                # 已过开场：不可退款（管理员/前台可关闭，但不退）
                if not is_staff:
                    return Response({'detail': '已过开场时间，不可取消'}, status=403)
                fee_amount = booking.amount
            elif (slot_start - now) > FREE_CANCEL_WINDOW:
                # 开场前 2 小时外：免费取消，全额退款（会员可自助）
                refund_amount = booking.amount
            else:
                # 开场前 2 小时内且未开场：扣 20% 手续费
                if not is_staff:
                    return Response({'detail': '距开场不足 2 小时，需联系管理员或前台取消'}, status=403)
                fee_amount = (booking.amount * CANCEL_FEE_RATE).quantize(Decimal('0.01'))
                refund_amount = booking.amount - fee_amount
        data = {}
        if refund_amount > 0:
            User.objects.filter(pk=user.pk).update(balance=F('balance') + refund_amount)
            user.refresh_from_db()
            Payment.objects.create(
                user=user,
                booking=booking,
                type=Payment.TYPE_REFUND,
                amount=refund_amount,
                method=Payment.METHOD_BALANCE,
                status=Payment.STATUS_SUCCESS,
            )
            data = {
                'refund_amount': str(refund_amount),
                'fee_amount': str(fee_amount),
                'balance': str(user.balance),
            }

        booking.status = 'cancelled'
        booking.fee_amount = fee_amount
        booking.save()
        invalidate(f'availability:{booking.court.venue_id}:{booking.date.isoformat()}')

        # 退款后消费减少，重算会员等级（手续费保留在累计消费中）
        if was_paid:
            user.refresh_level_from_spend()

        return Response({'code': 200, 'message': '已取消', 'data': data})

    @action(detail=False, methods=['get'])
    def my(self, request):
        qs = self.get_queryset().filter(user=request.user)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = BookingListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = BookingListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        """到店签到核销（仅管理员/前台）"""
        booking = self.get_object()
        if booking.status != 'paid':
            return Response({'detail': '只有已支付订单可签到'}, status=400)
        if booking.checked_in:
            return Response({'detail': '该订单已签到'}, status=400)
        if booking.date != timezone.localdate():
            return Response({'detail': '签到日期必须与预约日期一致'}, status=400)
        booking.checked_in = True
        booking.checked_in_at = timezone.now()
        booking.save(update_fields=['checked_in', 'checked_in_at'])
        return Response({'code': 200, 'message': '签到成功',
                         'data': {'checked_in_at': booking.checked_in_at.strftime('%Y-%m-%d %H:%M')}})

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """导出预约订单为 CSV（管理员/前台）"""
        qs = self.get_queryset()
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="bookings.csv"'
        writer = csv.writer(response)
        writer.writerow(['订单号', '用户', '手机号', '场馆', '场地', '日期', '时段',
                         '金额', '原价', '折扣率', '状态', '签到', '创建时间'])
        for b in qs:
            writer.writerow([
                b.id,
                b.user.nickname or b.user.phone,
                b.user.phone,
                b.court.venue.name,
                b.court.name,
                b.date,
                b.time_slot.display,
                b.amount,
                b.original_amount or '',
                b.discount_rate or '',
                b.get_status_display(),
                '已签到' if b.checked_in else '未签到',
                timezone.localtime(b.created_at).strftime('%Y-%m-%d %H:%M'),
            ])
        return response
