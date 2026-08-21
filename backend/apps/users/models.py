# users models
from django.contrib.auth.models import AbstractUser
from django.db import models
from decimal import Decimal


class User(AbstractUser):
    """Custom user model — 使用手机号作为登录标识"""

    ROLE_ADMIN = 'admin'
    ROLE_RECEPTION = 'reception'
    ROLE_MEMBER = 'member'
    ROLE_CHOICES = [
        (ROLE_ADMIN, '管理员'),
        (ROLE_RECEPTION, '前台'),
        (ROLE_MEMBER, '会员'),
    ]

    LEVEL_NORMAL = 'normal'
    LEVEL_SILVER = 'silver'
    LEVEL_GOLD = 'gold'
    LEVEL_CHOICES = [
        (LEVEL_NORMAL, '普通会员'),
        (LEVEL_SILVER, '银卡会员'),
        (LEVEL_GOLD, '金卡会员'),
    ]

    DISCOUNT_RATES = {
        LEVEL_NORMAL: Decimal('1.00'),
        LEVEL_SILVER: Decimal('0.95'),
        LEVEL_GOLD: Decimal('0.90'),
    }

    # 消费累计达到阈值自动升级会员等级
    LEVEL_UPGRADE_THRESHOLDS = {
        LEVEL_SILVER: Decimal('500'),
        LEVEL_GOLD: Decimal('2000'),
    }

    nickname = models.CharField('昵称', max_length=50, default='')
    phone = models.CharField('手机号', max_length=11, unique=True)
    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES, default=ROLE_MEMBER)
    level = models.CharField('会员等级', max_length=20, choices=LEVEL_CHOICES, default=LEVEL_NORMAL)
    balance = models.DecimalField('余额', max_digits=10, decimal_places=2, default=0)

    is_blacklisted = models.BooleanField('拉黑', default=False)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.phone
        super().save(*args, **kwargs)

    def get_discount_rate(self):
        if self.role != self.ROLE_MEMBER:
            return Decimal('1.00')
        return self.DISCOUNT_RATES.get(self.level, Decimal('1.00'))

    def get_total_spend(self):
        """累计消费金额（已支付订单）"""
        from django.db.models import Sum
        from apps.bookings.models import Booking
        agg = Booking.objects.filter(user=self, status='paid').aggregate(s=Sum('amount'))
        return agg['s'] or Decimal('0')

    def refresh_level_from_spend(self):
        """根据累计消费自动升级会员等级（只升级不降级），返回是否发生变化"""
        if self.role != self.ROLE_MEMBER:
            return False
        total = self.get_total_spend()
        target = self.LEVEL_NORMAL
        if total >= self.LEVEL_UPGRADE_THRESHOLDS[self.LEVEL_GOLD]:
            target = self.LEVEL_GOLD
        elif total >= self.LEVEL_UPGRADE_THRESHOLDS[self.LEVEL_SILVER]:
            target = self.LEVEL_SILVER
        order = [self.LEVEL_NORMAL, self.LEVEL_SILVER, self.LEVEL_GOLD]
        if order.index(target) > order.index(self.level):
            self.level = target
            self.save(update_fields=['level'])
            return True
        return False

    def __str__(self):
        return f"{self.nickname or self.phone} ({self.get_role_display()})"
