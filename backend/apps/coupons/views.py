from decimal import Decimal

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .models import Coupon, UserCoupon
from .serializers import CouponSerializer, UserCouponSerializer
from apps.users.models import User
from apps.users.permissions import IsAdmin

# 积分规则：支付/充值 1 元积 1 分；500 积分兑换 ¥5 券
POINTS_PER_YUAN = 1
REDEEM_POINTS = 500
REDEEM_AMOUNT = Decimal('5.00')
REDEEM_EXPIRY_DAYS = 30


class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer

    def get_permissions(self):
        if self.action in ('list', 'create', 'destroy'):
            return [IsAdmin()]
        return [IsAuthenticated()]

    @transaction.atomic
    @action(detail=True, methods=['post'])
    def claim(self, request, pk=None):
        """领取优惠券：行锁扣发行量，每人每券限领一张"""
        if request.user.role != 'member':
            return Response({'code': 400, 'message': '仅会员可领取优惠券'}, status=400)
        coupon = Coupon.objects.select_for_update().get(pk=pk)
        now = timezone.now()
        if not coupon.is_active:
            return Response({'code': 400, 'message': '该优惠券未启用'}, status=400)
        if coupon.expires_at <= now:
            return Response({'code': 400, 'message': '该优惠券已过期'}, status=400)
        if coupon.claimed >= coupon.total:
            return Response({'code': 400, 'message': '该优惠券已领完'}, status=400)
        if UserCoupon.objects.filter(user=request.user, coupon=coupon).exists():
            return Response({'code': 400, 'message': '你已领取过该优惠券'}, status=400)

        Coupon.objects.filter(pk=coupon.pk).update(claimed=F('claimed') + 1)
        uc = UserCoupon.objects.create(
            user=request.user, coupon=coupon,
            amount=coupon.amount, min_amount=coupon.min_amount, expires_at=coupon.expires_at,
        )
        return Response({'code': 200, 'message': '领取成功', 'data': UserCouponSerializer(uc).data})

    @action(detail=False, methods=['get'])
    def my(self, request):
        """我的优惠券"""
        qs = UserCoupon.objects.filter(user=request.user).select_related('coupon')
        status = request.query_params.get('status')
        if status:
            qs = qs.filter(status=status)
        return Response({'code': 200, 'data': UserCouponSerializer(qs, many=True).data})

    @transaction.atomic
    @action(detail=False, methods=['post'])
    def redeem(self, request):
        """积分兑换：500 积分换 ¥5 券（30 天有效）"""
        if request.user.role != 'member':
            return Response({'code': 400, 'message': '仅会员可兑换'}, status=400)
        user = User.objects.select_for_update().get(pk=request.user.pk)
        if user.points < REDEEM_POINTS:
            return Response({'code': 400, 'message': f'积分不足，需 {REDEEM_POINTS} 积分'}, status=400)
        user.points -= REDEEM_POINTS
        user.save(update_fields=['points'])
        uc = UserCoupon.objects.create(
            user=user, coupon=None, amount=REDEEM_AMOUNT, min_amount=Decimal('0'),
            expires_at=timezone.now() + timezone.timedelta(days=REDEEM_EXPIRY_DAYS),
        )
        return Response({'code': 200, 'message': '兑换成功',
                         'data': {'points': user.points, 'user_coupon': UserCouponSerializer(uc).data}})
