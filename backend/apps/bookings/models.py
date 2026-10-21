# bookings models

from datetime import datetime, timedelta

from django.db import models
from django.conf import settings
from django.utils import timezone


class Booking(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, '待支付'),
        (STATUS_PAID, '已支付'),
        (STATUS_CANCELLED, '已取消'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='用户',
    )
    court = models.ForeignKey(
        'venues.Court',
        on_delete=models.PROTECT,
        related_name='bookings',
        verbose_name='场地',
    )
    date = models.DateField(verbose_name='日期')
    time_slot = models.ForeignKey(
        'venues.TimeSlot',
        on_delete=models.PROTECT,
        related_name='bookings',
        verbose_name='时段',
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING,
        verbose_name='状态',
    )
    checked_in = models.BooleanField('已签到', default=False)
    checked_in_at = models.DateTimeField('签到时间', null=True, blank=True)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='金额',
    )
    original_amount = models.DecimalField(
        '原价', max_digits=10, decimal_places=2, null=True, blank=True,
    )
    discount_rate = models.DecimalField(
        '折扣率', max_digits=4, decimal_places=2, null=True, blank=True,
    )
    fee_amount = models.DecimalField(
        '手续费', max_digits=10, decimal_places=2, default=0,
    )
    # 优惠券快照：下单时锁定金额，支付成功时才核销券（取消待支付订单不损失券）
    user_coupon = models.ForeignKey(
        'coupons.UserCoupon', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='bookings', verbose_name='使用的优惠券',
    )
    coupon_amount = models.DecimalField('券抵扣', max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'bookings'
        verbose_name = '预约订单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['court', 'date']),
            models.Index(fields=['date', 'status']),
        ]

    @property
    def slot_start_at(self):
        """时段开始的具体时刻（当天 + 时段起点，带时区）"""
        return datetime.combine(
            self.date, self.time_slot.start_time,
            tzinfo=timezone.get_current_timezone(),
        )

    @property
    def slot_end_at(self):
        """时段结束的具体时刻（当天 + 时段终点，带时区）"""
        return datetime.combine(
            self.date, self.time_slot.end_time,
            tzinfo=timezone.get_current_timezone(),
        )

    @property
    def is_finished(self):
        """已支付且时段已经结束：订单视作结束，不再可支付/签到/退场"""
        return self.status == self.STATUS_PAID and timezone.now() >= self.slot_end_at

    @property
    def is_expired(self):
        """待支付但已超过支付时限：订单视作结束（超时未支付）"""
        from .utils import PENDING_TIMEOUT_MINUTES

        if self.status != self.STATUS_PENDING:
            return False
        deadline = self.created_at + timedelta(minutes=PENDING_TIMEOUT_MINUTES)
        return timezone.now() >= deadline

    def __str__(self):
        return f"{self.user.nickname or self.user.phone} @ {self.court.name} {self.date}"


class CancellationRequest(models.Model):
    """退场申请：会员在开场前 2 小时内提交，前台审批通过后 5 分钟自动退款"""
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_REFUNDED = 'refunded'
    STATUS_CHOICES = [
        (STATUS_PENDING, '待审批'),
        (STATUS_APPROVED, '已通过'),
        (STATUS_REJECTED, '已驳回'),
        (STATUS_REFUNDED, '已退款'),
    ]

    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name='cancellation_requests',
        verbose_name='订单',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='cancellation_requests', verbose_name='用户',
    )
    reason = models.CharField('申请原因', max_length=200, default='', blank=True)
    refund_amount = models.DecimalField('应退金额', max_digits=10, decimal_places=2, default=0)
    fee_amount = models.DecimalField('手续费', max_digits=10, decimal_places=2, default=0)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    reject_reason = models.CharField('驳回原因', max_length=200, default='', blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reviewed_cancellation_requests', verbose_name='审批人',
    )
    reviewed_at = models.DateTimeField('审批时间', null=True, blank=True)
    refund_at = models.DateTimeField('计划退款时间', null=True, blank=True)
    refunded_at = models.DateTimeField('实际退款时间', null=True, blank=True)
    created_at = models.DateTimeField('申请时间', auto_now_add=True)

    class Meta:
        db_table = 'cancellation_requests'
        verbose_name = '退场申请'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'refund_at']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f'{self.user.phone} 退场申请 #{self.booking_id} ({self.get_status_display()})'
