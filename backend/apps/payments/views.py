import csv
from decimal import Decimal

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone

from .models import Payment
from .serializers import (
    PaymentListSerializer, PaymentDetailSerializer,
    RechargeSerializer, PayBookingSerializer,
)
from apps.users.permissions import IsAdminOrReception
from apps.bookings.models import Booking

# 充值赠送档位：充满 threshold 送 gift（取最高档）
RECHARGE_BONUS_TIERS = [
    (Decimal('100'), Decimal('10')),
    (Decimal('300'), Decimal('40')),
    (Decimal('500'), Decimal('80')),
    (Decimal('1000'), Decimal('200')),
]


def get_recharge_bonus(amount):
    bonus = Decimal('0')
    for threshold, gift in RECHARGE_BONUS_TIERS:
        if amount >= threshold:
            bonus = gift
    return bonus


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related(
        'user', 'booking', 'booking__court', 'booking__court__venue'
    ).all()

    def get_serializer_class(self):
        if self.action == 'list':
            return PaymentListSerializer
        return PaymentDetailSerializer

    def get_permissions(self):
        if self.action in ('create', 'pay', 'recharge', 'list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAdminOrReception()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'member':
            qs = qs.filter(user=user)
        type_filter = self.request.query_params.get('type')
        if type_filter:
            qs = qs.filter(type=type_filter)
        return qs

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def recharge(self, request):
        """Recharge balance for current user（支持充值赠送）"""
        serializer = RechargeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data['amount']
        method = serializer.validated_data['method']
        user = request.user

        bonus = get_recharge_bonus(amount)
        user.balance += amount + bonus
        user.save(update_fields=['balance'])

        # Create payment record（amount 为充值本金，bonus 为赠送）
        payment = Payment.objects.create(
            user=user, type=Payment.TYPE_RECHARGE,
            amount=amount, bonus=bonus, method=method,
            status=Payment.STATUS_SUCCESS,
        )

        return Response({
            'code': 200, 'message': '充值成功',
            'data': {
                'payment_id': payment.id,
                'balance': user.balance,
                'bonus': bonus,
                'credited': amount + bonus,
            },
        })

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def pay(self, request):
        """Pay for a booking"""
        serializer = PayBookingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking_id = serializer.validated_data['booking_id']
        method = serializer.validated_data['method']
        user = request.user

        try:
            booking = Booking.objects.select_for_update().get(
                id=booking_id, user=user,
            )
        except Booking.DoesNotExist:
            return Response({'code': 400, 'message': '订单不存在'}, status=400)

        if booking.status != 'pending':
            return Response({'code': 400, 'message': '订单状态不正确，当前状态：' + booking.get_status_display()}, status=400)

        if method == 'balance':
            if user.balance < booking.amount:
                return Response({'code': 400, 'message': '余额不足，当前余额：¥' + str(user.balance)}, status=400)
            user.balance -= booking.amount
            user.save(update_fields=['balance'])

        booking.status = 'paid'
        booking.save(update_fields=['status'])

        payment = Payment.objects.create(
            user=user, booking=booking, type=Payment.TYPE_BOOKING,
            amount=booking.amount, method=method,
            status=Payment.STATUS_SUCCESS,
        )

        # 消费后自动升级会员等级
        upgraded = user.refresh_level_from_spend()

        return Response({
            'code': 200, 'message': '支付成功',
            'data': {
                'payment_id': payment.id,
                'balance': user.balance,
                'booking_status': booking.status,
                'level_upgraded': upgraded,
                'level': user.level,
            },
        })

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """导出支付记录为 CSV（管理员/前台）"""
        qs = self.get_queryset()
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="payments.csv"'
        writer = csv.writer(response)
        writer.writerow(['记录ID', '用户', '手机号', '类型', '金额', '赠送', '支付方式',
                         '状态', '关联订单', '时间'])
        for p in qs:
            writer.writerow([
                p.id,
                p.user.nickname or p.user.phone,
                p.user.phone,
                p.get_type_display(),
                p.amount,
                p.bonus or '0',
                p.get_method_display(),
                p.get_status_display(),
                f'#{p.booking_id}' if p.booking_id else '-',
                timezone.localtime(p.created_at).strftime('%Y-%m-%d %H:%M'),
            ])
        return response
