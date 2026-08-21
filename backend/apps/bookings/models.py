# bookings models

from django.db import models
from django.conf import settings


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

    def __str__(self):
        return f"{self.user.nickname or self.user.phone} @ {self.court.name} {self.date}"
