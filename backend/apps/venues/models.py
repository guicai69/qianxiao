# venues models
from django.db import models


class BaseModel(models.Model):
    """项目公共基类 — 所有 Model 必须继承"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        abstract = True


class Venue(BaseModel):
    """场馆"""
    name = models.CharField('场馆名称', max_length=100, unique=True)
    address = models.CharField('地址', max_length=255, default='', blank=True)
    phone = models.CharField('联系电话', max_length=20, default='', blank=True)
    description = models.TextField('描述', default='', blank=True)
    is_active = models.BooleanField('启用', default=True)

    class Meta:
        db_table = 'venues'
        verbose_name = '场馆'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Court(BaseModel):
    """场地 — 属于某个场馆"""
    venue = models.ForeignKey(
        Venue,
        on_delete=models.CASCADE,
        related_name='courts',
        verbose_name='所属场馆',
    )
    name = models.CharField('场地名称', max_length=50)
    is_active = models.BooleanField('启用', default=True)

    class Meta:
        db_table = 'courts'
        verbose_name = '场地'
        verbose_name_plural = verbose_name
        ordering = ['venue', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['venue', 'name'],
                name='uq_venue_court_name',
            ),
        ]

    def __str__(self):
        return f"{self.venue.name} - {self.name}"


class TimeSlot(BaseModel):
    """时段 — 属于某个场馆，每个场馆可独立定价"""
    venue = models.ForeignKey(
        Venue,
        on_delete=models.CASCADE,
        related_name='time_slots',
        verbose_name='所属场馆',
    )
    start_time = models.TimeField('开始时间')
    end_time = models.TimeField('结束时间')
    price = models.DecimalField('价格', max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField('启用', default=True)

    class Meta:
        db_table = 'time_slots'
        verbose_name = '时段'
        verbose_name_plural = verbose_name
        ordering = ['venue', 'start_time']
        constraints = [
            models.UniqueConstraint(
                fields=['venue', 'start_time', 'end_time'],
                name='uq_venue_slot_time',
            ),
        ]

    def __str__(self):
        return f"{self.venue.name} {self.start_time:%H:%M}-{self.end_time:%H:%M} ¥{self.price}"

    @property
    def display(self):
        return f"{self.start_time:%H:%M}-{self.end_time:%H:%M}"
