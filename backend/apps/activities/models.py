# activities models
from django.conf import settings
from django.db import models


class Activity(models.Model):
    """活动/赛事/培训/教练课 —— 教练预约复用本模型（type=coach）"""
    TYPE_MATCH = 'match'
    TYPE_TRAINING = 'training'
    TYPE_COACH = 'coach'
    TYPE_CHOICES = [
        (TYPE_MATCH, '比赛'),
        (TYPE_TRAINING, '培训'),
        (TYPE_COACH, '教练课'),
    ]

    venue = models.ForeignKey(
        'venues.Venue', on_delete=models.PROTECT, related_name='activities',
        verbose_name='场馆',
    )
    type = models.CharField('类型', max_length=20, choices=TYPE_CHOICES, default=TYPE_MATCH)
    title = models.CharField('标题', max_length=100)
    description = models.TextField('说明', default='', blank=True)
    start_at = models.DateTimeField('开始时间')
    end_at = models.DateTimeField('结束时间')
    price = models.DecimalField('价格', max_digits=10, decimal_places=2, default=0)
    capacity = models.PositiveIntegerField('名额')
    registered = models.PositiveIntegerField('已报名', default=0)
    deadline = models.DateTimeField('报名截止')
    is_active = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'activities'
        verbose_name = '活动'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Registration(models.Model):
    """活动报名（取消后名额释放，可重新报名）"""
    STATUS_REGISTERED = 'registered'
    STATUS_CANCELLED = 'cancelled'
    STATUS_ATTENDED = 'attended'
    STATUS_CHOICES = [
        (STATUS_REGISTERED, '已报名'),
        (STATUS_CANCELLED, '已取消'),
        (STATUS_ATTENDED, '已到场'),
    ]

    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, related_name='registrations',
        verbose_name='活动',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='registrations',
        verbose_name='用户',
    )
    price = models.DecimalField('报名费快照', max_digits=10, decimal_places=2, default=0)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default=STATUS_REGISTERED)
    created_at = models.DateTimeField('报名时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'registrations'
        verbose_name = '活动报名'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['activity', 'status']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f'{self.user.phone} @ {self.activity.title}'
