from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from .models import Booking

PENDING_TIMEOUT_MINUTES = 15
FREE_CANCEL_WINDOW = timedelta(hours=2)
CANCEL_FEE_RATE = Decimal('0.2')


def cancel_expired_pendings():
    """取消超过 15 分钟未支付的预约订单，返回取消数量。"""
    threshold = timezone.now() - timedelta(minutes=PENDING_TIMEOUT_MINUTES)
    return Booking.objects.filter(
        status='pending', created_at__lt=threshold,
    ).update(status='cancelled', updated_at=timezone.now())
