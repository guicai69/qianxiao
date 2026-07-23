# users models
from django.contrib.auth.models import AbstractUser
from django.db import models


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
    LEVEL_GOLD = 'gold'
    LEVEL_CHOICES = [
        (LEVEL_NORMAL, '普通会员'),
        (LEVEL_GOLD, '金卡会员'),
    ]

    nickname = models.CharField('昵称', max_length=50, default='')
    phone = models.CharField('手机号', max_length=11, unique=True)
    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES, default=ROLE_MEMBER)
    level = models.CharField('会员等级', max_length=20, choices=LEVEL_CHOICES, default=LEVEL_NORMAL)
    balance = models.DecimalField('余额', max_digits=10, decimal_places=2, default=0)

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

    def __str__(self):
        return f"{self.nickname or self.phone} ({self.get_role_display()})"
