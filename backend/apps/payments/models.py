# payments models
from django.db import models
from django.conf import settings


class Payment(models.Model):
    TYPE_RECHARGE = 'recharge'
    TYPE_BOOKING = 'booking'
    TYPE_REFUND = 'refund'
    TYPE_CHOICES = [
        (TYPE_RECHARGE, '充值'),
        (TYPE_BOOKING, '消费'),
        (TYPE_REFUND, '退款'),
    ]

    METHOD_BALANCE = 'balance'
    METHOD_WECHAT = 'wechat'
    METHOD_ALIPAY = 'alipay'
    METHOD_CASH = 'cash'
    METHOD_CHOICES = [
        (METHOD_BALANCE, '余额支付'),
        (METHOD_WECHAT, '微信支付'),
        (METHOD_ALIPAY, '支付宝'),
        (METHOD_CASH, '现金'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, '处理中'),
        (STATUS_SUCCESS, '成功'),
        (STATUS_FAILED, '失败'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='用户',
    )
    booking = models.ForeignKey(
        'bookings.Booking',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='payments',
        verbose_name='关联订单',
    )
    type = models.CharField('类型', max_length=20, choices=TYPE_CHOICES, default=TYPE_BOOKING)
    amount = models.DecimalField('金额', max_digits=10, decimal_places=2)
    bonus = models.DecimalField('赠送金额', max_digits=10, decimal_places=2, default=0)
    method = models.CharField('支付方式', max_length=20, choices=METHOD_CHOICES, default=METHOD_BALANCE)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default=STATUS_SUCCESS)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'payments'
        verbose_name = '支付记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'type']),
            models.Index(fields=['booking']),
        ]

    def __str__(self):
        return f"{self.user.nickname or self.user.phone} {self.get_type_display()} ¥{self.amount}"
