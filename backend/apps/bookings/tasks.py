from celery import shared_task

from apps.bookings.utils import cancel_expired_pendings


@shared_task(name='bookings.cancel_expired_pendings')
def cancel_expired_bookings_task():
    """beat 周期任务：取消超过 15 分钟未支付的订单，返回取消数量"""
    return cancel_expired_pendings()
