from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from .models import Booking

PENDING_TIMEOUT_MINUTES = 15
FREE_CANCEL_WINDOW = timedelta(hours=2)
CANCEL_FEE_RATE = Decimal('0.2')
# 退场申请：前台/管理员通过后立刻退款；提交超过 5 分钟仍无人处理则自动通过并退款
AUTO_APPROVE_DELAY = timedelta(minutes=5)


def cancel_expired_pendings():
    """取消超过 15 分钟未支付的预约订单，返回取消数量。"""
    threshold = timezone.now() - timedelta(minutes=PENDING_TIMEOUT_MINUTES)
    return Booking.objects.filter(
        status='pending', created_at__lt=threshold,
    ).update(status='cancelled', updated_at=timezone.now())


def auto_approve_stale_requests(now=None):
    """把提交超过 AUTO_APPROVE_DELAY 仍无人处理的退场申请自动通过（无审批人）。

    返回自动通过的数量。created_at 是 auto_now_add，测试里可用 queryset.update 改写。
    """
    from .models import CancellationRequest

    now = now or timezone.now()
    return CancellationRequest.objects.filter(
        status=CancellationRequest.STATUS_PENDING,
        created_at__lte=now - AUTO_APPROVE_DELAY,
    ).update(
        status=CancellationRequest.STATUS_APPROVED,
        reviewed_at=now,
        refund_at=now,
    )


def settle_refund(req_id, now=None):
    """结算一条已通过的退场申请：应退金额入余额 → 订单置 cancelled → 申请置 refunded。

    返回被结算的申请对象；申请已不是 approved（被并发处理）时返回 None。
    """
    from django.db import transaction
    from django.db.models import F

    from .models import CancellationRequest
    from apps.payments.models import Payment
    from apps.users.models import User

    now = now or timezone.now()
    with transaction.atomic():
        req = CancellationRequest.objects.select_for_update().select_related(
            'booking', 'user',
        ).filter(pk=req_id, status=CancellationRequest.STATUS_APPROVED).first()
        if not req:
            return None
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
        return req


def process_cancellation_requests(now=None):
    """退场申请统一结算入口：① 待审批超时的自动通过；② 所有已通过的立刻退款。

    返回本次退款的申请数量。惰性调用（进退场申请/我的订单页）与 Celery beat 每分钟各跑一次。
    """
    from .models import CancellationRequest

    now = now or timezone.now()
    auto_approve_stale_requests(now)
    ids = list(CancellationRequest.objects.filter(
        status=CancellationRequest.STATUS_APPROVED,
    ).values_list('id', flat=True))
    return sum(1 for req_id in ids if settle_refund(req_id, now))
