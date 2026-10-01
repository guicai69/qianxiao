"""Celery 应用：beat 每 5 分钟清理超过 15 分钟未支付的预约订单。

Windows 启动（solo 池）：
    celery -A config worker -l info --pool=solo
    celery -A config beat -l info
"""
import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

app = Celery('badminton_venue')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
