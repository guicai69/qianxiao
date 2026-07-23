# users models
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model — will be extended in phase 2."""
    phone = models.CharField('手机号', max_length=11, unique=True, null=True, blank=True)
    role = models.CharField('角色', max_length=20, default='member')
    level = models.CharField('会员等级', max_length=20, default='normal')
    balance = models.DecimalField('余额', max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username or self.phone or str(self.id)
