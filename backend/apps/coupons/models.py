# coupons models
from decimal import Decimal

from django.conf import settings
from django.db import models


class Coupon(models.Model):
    """优惠券模板（管理员发行）"""
    name = models.CharField('名称', max_length=50)
    amount = models.DecimalField('面额', max_digits=10, decimal_places=2)
    min_amount = models.DecimalField('满减阈值', max_digits=10, decimal_places=2, default=0)
    total = models.PositiveIntegerField('发行量')
    claimed = models.PositiveIntegerField('已领取', default=0)
    expires_at = models.DateTimeField('有效期至')
    is_active = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'coupons'
        verbose_name = '优惠券'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ¥{self.amount}'


class UserCoupon(models.Model):
    """用户持有的券（领取时快照面额/门槛/有效期；积分兑换的券 coupon 为空）"""
    STATUS_UNUSED = 'unused'
    STATUS_USED = 'used'
    STATUS_CHOICES = [
        (STATUS_UNUSED, '未使用'),
        (STATUS_USED, '已使用'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_coupons',
        verbose_name='用户',
    )
    coupon = models.ForeignKey(
        Coupon, on_delete=models.PROTECT, related_name='user_coupons',
        null=True, blank=True, verbose_name='券模板',
    )
    amount = models.DecimalField('面额', max_digits=10, decimal_places=2)
    min_amount = models.DecimalField('满减阈值', max_digits=10, decimal_places=2, default=0)
    expires_at = models.DateTimeField('有效期至')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default=STATUS_UNUSED)
    claimed_at = models.DateTimeField('领取时间', auto_now_add=True)
    used_at = models.DateTimeField('使用时间', null=True, blank=True)

    class Meta:
        db_table = 'user_coupons'
        verbose_name = '用户优惠券'
        verbose_name_plural = verbose_name
        ordering = ['-claimed_at']
        indexes = [
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f'{self.user.phone} ¥{self.amount}'
