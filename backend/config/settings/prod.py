"""Production environment settings.

用法：设置环境变量 DJANGO_SETTINGS_MODULE=config.settings.prod 后启动
（gunicorn 配置见 backend/gunicorn.conf.py，部署文档见 docs/deploy.md）。
"""
import os

from .base import *  # noqa: F401, F403

DEBUG = False
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
CORS_ALLOW_ALL_ORIGINS = os.environ.get('CORS_ALLOW_ALL', '0') == '1'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
