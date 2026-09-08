# backend — Django 后端

羽毛球馆管理系统的后端服务，基于 **Django 5 + Django REST Framework** 提供 RESTful API。

## 技术栈

- Python 3.11 · Django 5.0 · Django REST Framework 3.15
- SimpleJWT：JWT 认证 + 黑名单
- drf-spectacular：自动生成 Swagger 接口文档
- MySQL 8.4（数据库）· Redis + django-redis（可选缓存）

## 目录结构

```text
backend/
├── manage.py                   # Django 入口
├── requirements.txt            # 后端依赖
├── config/                     # 配置与路由
│   ├── settings/base.py        # 公共配置（DB / JWT / CORS / DRF）
│   ├── settings/dev.py         # 开发覆写
│   ├── urls.py                 # 根路由 + Swagger
│   └── api_urls.py             # API 路由聚合
└── apps/
    ├── users/                  # 用户、角色、认证
    ├── venues/                 # 场馆、场地、时段
    ├── bookings/               # 预约订单 + 冲突检测
    ├── payments/               # 充值、消费、退款
    ├── stats/                  # 数据统计
    └── announcements/          # 系统公告
```

## 启动

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

## 接口文档

启动后访问 Swagger UI：<http://localhost:8000/api/docs/>
