from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from .models import Booking

PENDING_TIMEOUT_MINUTES = 15
FREE_CANCEL_WINDOW = timedelta(hours=2)
CANCEL_FEE_RATE = Decimal('0.2')
# 退场申请：前台审批通过后，延迟 5 分钟自动退款
REFUND_DELAY = timedelta(minutes=5)


def cancel_expired_pendings():
    """取消超过 15 分钟未支付的预约订单，返回取消数量。"""
    threshold = timezone.now() - timedelta(minutes=PENDING_TIMEOUT_MINUTES)
    return Booking.objects.filter(
        status='pending', created_at__lt=threshold,
    ).update(status='cancelled', updated_at=timezone.now())


def process_due_refunds():
    """处理到期的退场申请：审批通过 5 分钟后自动退款并取消订单，返回处理数量。"""
    from django.db import transaction
    from django.db.models import F

    from .models import CancellationRequest
    from apps.payments.models import Payment
    from apps.users.models import User

    now = timezone.now()
    ids = list(CancellationRequest.objects.filter(
        status=CancellationRequest.STATUS_APPROVED,
        refund_at__lte=now,
    ).values_list('id', flat=True))

    count = 0
    for req_id in ids:
        with transaction.atomic():
            req = CancellationRequest.objects.select_for_update().select_related(
                'booking', 'user',
            ).filter(pk=req_id, status=CancellationRequest.STATUS_APPROVED).first()
            if not req:
                continue
            booking = req.booking
            user = req.user
            if booking.status == 'paid':
                if req.refund_amount > 0:
                    User.objects.filter(pk=user.pk).update(balance=F('balance') + req.refund_amount)
                    user.refresh_from_db()
                    Payment.objects.create(
                        user=user, booking=booking, type=Payment.TYPE_REFUND,
                        amount=req.refund_amount, method=Payment.METHOD_BALANCE,
                        status=Payment.STATUS_SUCCESS,
                    )
                booking.status = 'cancelled'
                booking.fee_amount = req.fee_amount
                booking.save()
                user.refresh_level_from_spend()
            req.status = CancellationRequest.STATUS_REFUNDED
            req.refunded_at = now
            req.save(update_fields=['status', 'refunded_at'])
            count += 1
    return count
