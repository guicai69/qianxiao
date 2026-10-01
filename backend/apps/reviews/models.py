# reviews models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Review(models.Model):
    """订单评价：仅已支付且已签到的订单可评，每订单限一条（OneToOne 保证）"""
    booking = models.OneToOneField(
        'bookings.Booking', on_delete=models.CASCADE, related_name='review',
        verbose_name='订单',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews',
        verbose_name='用户',
    )
    rating = models.PositiveSmallIntegerField(
        '评分', validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    content = models.TextField('评价内容', default='', blank=True)
    reply = models.TextField('商家回复', default='', blank=True)
    replied_at = models.DateTimeField('回复时间', null=True, blank=True)
    created_at = models.DateTimeField('评价时间', auto_now_add=True)

    class Meta:
        db_table = 'reviews'
        verbose_name = '订单评价'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f'{self.user.phone} {self.rating}星'


class Favorite(models.Model):
    """场馆收藏（幂等：同一用户同一场馆仅一条）"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites',
        verbose_name='用户',
    )
    venue = models.ForeignKey(
        'venues.Venue', on_delete=models.PROTECT, related_name='favorites',
        verbose_name='场馆',
    )
    created_at = models.DateTimeField('收藏时间', auto_now_add=True)

    class Meta:
        db_table = 'favorites'
        verbose_name = '场馆收藏'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'venue'], name='uq_user_venue_favorite'),
        ]

    def __str__(self):
        return f'{self.user.phone} 收藏 {self.venue.name}'


class Feedback(models.Model):
    """意见反馈"""
    STATUS_PENDING = 'pending'
    STATUS_PROCESSED = 'processed'
    STATUS_CHOICES = [
        (STATUS_PENDING, '待处理'),
        (STATUS_PROCESSED, '已处理'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedbacks',
        verbose_name='用户',
    )
    content = models.TextField('反馈内容')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    reply = models.TextField('处理回复', default='', blank=True)
    created_at = models.DateTimeField('提交时间', auto_now_add=True)
    processed_at = models.DateTimeField('处理时间', null=True, blank=True)

    class Meta:
        db_table = 'feedbacks'
        verbose_name = '意见反馈'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.phone}: {self.content[:20]}'
