import csv

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import F
from django.http import HttpResponse
from django.utils import timezone
from decimal import Decimal

from .models import Booking
from .serializers import (
    BookingListSerializer, BookingDetailSerializer,
    BookingCreateSerializer, BookingUpdateStatusSerializer,
)
from apps.payments.models import Payment
from apps.users.permissions import IsAdmin, IsAdminOrReception

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

        # Filters
        venue = self.request.query_params.get('venue')
        if venue:
            qs = qs.filter(court__venue_id=venue)

        bdate = self.request.query_params.get('date')
        if bdate:
            qs = qs.filter(date=bdate)

        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        return qs.order_by('-created_at')

    def perform_create(self, serializer):
        court = serializer.validated_data['court']
        time_slot = serializer.validated_data['time_slot']
        original_amount = time_slot.price
        discount_rate = self.request.user.get_discount_rate()
        amount = (original_amount * discount_rate).quantize(Decimal('0.01'))
        serializer.save(
            user=self.request.user,
            amount=amount,
            original_amount=original_amount,
            discount_rate=discount_rate,
        )

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status == 'cancelled':
            return Response({'detail': '该订单已取消'}, status=400)
        if booking.status == 'paid' and request.user.role not in ('admin', 'reception'):
            return Response(
                {'detail': '已支付订单需由管理员或前台确认后取消'},
                status=403,
            )
        if booking.status not in ['pending', 'paid']:
            return Response({'detail': '该订单状态不可取消'}, status=400)

        data = {}
        refunded_user = None
        if booking.status == 'paid':
            booking = Booking.objects.select_for_update().select_related('user').get(pk=booking.pk)
            user = booking.user
            User.objects.filter(pk=user.pk).update(balance=F('balance') + booking.amount)
            user.refresh_from_db()
            Payment.objects.create(
                user=user,
                booking=booking,
                type=Payment.TYPE_REFUND,
                amount=booking.amount,
                method=Payment.METHOD_BALANCE,
                status=Payment.STATUS_SUCCESS,
            )
            refunded_user = user
            data = {
                'refund_amount': str(booking.amount),
                'balance': str(user.balance),
            }

        booking.status = 'cancelled'
        booking.save(update_fields=['status'])

        # 退款后消费减少，重算会员等级
        if refunded_user:
            refunded_user.refresh_level_from_spend()

        return Response({'code': 200, 'message': '已取消', 'data': data})

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        booking = self.get_object()
        if booking.status != 'pending':
            return Response({'error': '只有待支付订单可支付'}, status=400)
        booking.status = 'paid'
        booking.save(update_fields=['status'])
        return Response({'code': 200, 'message': '已支付'})

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
