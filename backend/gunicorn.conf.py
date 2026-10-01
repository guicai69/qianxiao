"""gunicorn 配置（Linux 生产环境；Windows 用 waitress，见 docs/deploy.md）。

启动：gunicorn -c gunicorn.conf.py config.wsgi:application
"""
import multiprocessing

bind = '127.0.0.1:8000'
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
timeout = 60
accesslog = '-'
errorlog = '-'
