# 生产部署文档

> 目标：把「开发版 runserver 直跑」换成可答辩演示、可重启、可备份的生产形态。
> 两种路线：Windows（本机答辩环境）与 Ubuntu（云服务器）。

## 1. 环境变量（两平台通用）

| 变量 | 默认（开发） | 生产建议 |
|------|-------------|----------|
| `DJANGO_SETTINGS_MODULE` | `config.settings.dev` | `config.settings.prod` |
| `DJANGO_DEBUG` | `1` | `0` |
| `DJANGO_SECRET_KEY` | 内置开发密钥 | 随机 50 位 |
| `DJANGO_ALLOWED_HOSTS` | `*` | `你的域名,IP` |
| `CORS_ALLOW_ALL` | `1` | `0` |
| `DJANGO_CAPTCHA_REQUIRED` | `1` | `1` |
| `DJANGO_REDIS_URL` | `redis://127.0.0.1:6379/1` | 按需 |
| `CELERY_BROKER_URL` | `redis://127.0.0.1:6379/2` | 按需 |
| `DJANGO_LOG_LEVEL` | `INFO` | `WARNING` |

依赖：Python 3.11、MySQL 8.4（库名 `badminton_venue`）、Redis（缓存/验证码/Celery 共用，掉线自动降级）。

## 2. Windows 部署（答辩机）

1. 依赖：`pip install -r backend/requirements.txt waitress`。
2. 前端构建：`cd frontend && npm run build` → `dist/`。
3. 静态文件：`cd backend && python manage.py collectstatic --noinput`。
4. 后端（waitress 替代 runserver，进程守护用 NSSM 或任务计划程序）：
   ```powershell
   $env:DJANGO_SETTINGS_MODULE='config.settings.prod'
   $env:DJANGO_DEBUG='0'
   $env:DJANGO_SECRET_KEY='<随机50位>'
   $env:DJANGO_ALLOWED_HOSTS='localhost,127.0.0.1'
   waitress-serve --listen=0.0.0.0:8000 config.wsgi:application
   ```
5. 前端托管：直接 `npx serve dist` 或装 Nginx for Windows 用 `deploy/nginx.conf`（改 root 路径）。
6. 定时任务（取消过期订单，二选一）：
   - Celery：`celery -A config worker -l info --pool=solo` + `celery -A config beat -l info`
   - 计划任务（无 Celery 兜底）：`schtasks /create /tn badminton-expire /sc minute /mo 5 /tr "cd /d C:\path\backend && ..\.venv\Scripts\python.exe manage.py cancel_expired_bookings"`
7. 备份：`mysqldump -uroot -p123456 badminton_venue > backup_YYYYMMDD.sql`（每日计划任务）。

## 3. Ubuntu 部署（云服务器）

```bash
# 依赖与目录
sudo apt install python3-venv nginx redis-server mysql-server
mkdir -p /opt/badminton && cd /opt/badminton

# 后端
python3 -m venv .venv && .venv/bin/pip install -r backend/requirements.txt gunicorn
export DJANGO_SETTINGS_MODULE=config.settings.prod DJANGO_DEBUG=0 \
       DJANGO_SECRET_KEY='<随机50位>' DJANGO_ALLOWED_HOSTS='你的域名'
cd backend && .venv/bin/python manage.py migrate && .venv/bin/python manage.py collectstatic --noinput

# systemd 守护 gunicorn（/etc/systemd/system/badminton.service）
# ExecStart=/opt/badminton/.venv/bin/gunicorn -c /opt/badminton/backend/gunicorn.conf.py config.wsgi:application

# Nginx：cp deploy/nginx.conf /etc/nginx/sites-available/badminton && ln -s …/sites-enabled/ && nginx -t && systemctl reload nginx

# 前端：cd frontend && npm run build（dist 目录即 Nginx root）

# Celery（systemd 两个单元）：worker --pool=solo 与 beat，命令同 Windows
```

## 4. 上线检查清单

- [ ] `manage.py check --deploy` 无高危项
- [ ] `DEBUG=0`、SECRET_KEY 非内置、ALLOWED_HOSTS 收敛、CORS 白名单
- [ ] MySQL/Redis/Nginx/gunicorn(waitress)/Celery 全部开机自启
- [ ] 备份脚本存在且近 24h 执行过
- [ ] 登录/预约/支付/看板四条链路手工冒烟通过
