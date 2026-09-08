# announcements models
from django.db import models


class Announcement(models.Model):
    """系统公告 — 管理端发布，会员端展示"""

    title = models.CharField('标题', max_length=100)
    content = models.TextField('内容')
    is_published = models.BooleanField('发布', default=True)
    is_pinned = models.BooleanField('置顶', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'announcements'
        verbose_name = '公告'
        verbose_name_plural = verbose_name
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title
