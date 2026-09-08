# 🏸 羽毛球馆管理系统

> **Badminton Venue Management System** — 毕业设计项目

基于 **Django REST Framework + Vue 3** 的前后端分离多场馆预约管理系统，覆盖多场馆、多场地、多时段预约、会员等级与折扣、余额充值、模拟支付、到店签到核销、数据统计看板等完整业务闭环。

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.0-092E20?logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-3.15-092E20)
![Vue](https://img.shields.io/badge/Vue-3.5-4FC08D?logo=vue.js&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-8-646CFF?logo=vite&logoColor=white)
![Element Plus](https://img.shields.io/badge/Element_Plus-2.14-409EFF?logo=element&logoColor=white)
![Pinia](https://img.shields.io/badge/Pinia-4-ffd859)
![ECharts](https://img.shields.io/badge/ECharts-6-AA344D)
![MySQL](https://img.shields.io/badge/MySQL-8.4-4479A1?logo=mysql&logoColor=white)

</div>

## ✨ 功能特性

### 👥 用户与权限

- 三类角色：**管理员 / 前台 / 会员**，基于 JWT 的角色权限体系。
- 注册、登录、修改密码、个人信息管理。
- JWT 黑名单 + 禁用用户 Token 自动失效。

### 🏅 会员等级与折扣

| 等级 | 折扣 |
|------|------|
| 普通会员 `normal` | 原价 100% |
| 银卡会员 `silver` | 95 折 |
| 金卡会员 `gold` | 90 折 |

- 折扣在创建预约时写入订单快照，后续等级变化不影响已生成订单。
- 累计消费满 ¥500 自动升银卡、满 ¥2000 升金卡（只升不降）。

### 🏟 场馆、场地与时段

- 场馆 / 场地 / 时段 CRUD，支持按场馆查看场地。
- 时段独立定价（¥30–120）。
- 内置广州地区 5 个场馆示例数据。

### 📅 预约与订单

- 会员按日期、场馆、场地、时段在线预约。
- 同一场地同一日期同一时段自动冲突检测。
- 待支付订单可由会员自行取消；已支付订单需管理员/前台确认取消。
- 取消已支付订单时自动退款到余额，并生成退款记录。

### 💰 支付与余额

- 支持余额、微信、支付宝三种模拟支付方式。
- 余额充值 + 充值赠送（充 100 送 10、充 300 送 40、充 500 送 80、充 1000 送 200）。
- 管理端支付记录展示手机号、昵称、类型、金额、赠送、支付方式、关联订单。

### 📢 公告、签到与导出

- 系统公告：管理端发布 / 置顶 / 下线，会员端首页展示。
- 到店签到核销：已支付订单由管理员/前台签到，会员端查看签到状态。
- 数据导出：预约订单、支付记录一键导出 CSV（Excel 可直接打开）。

### 📊 数据统计

- 今日预约数、待处理数、今日营收、累计营收等总览指标。
- 近 7 日营收趋势（折线 + 柱状）、热门时段（横向柱状）、场地使用统计。
- 前台操作台每 5 秒自动刷新，页面重新可见时立即同步。

## 🖼 界面预览

> 📸 界面截图待补充，将截图放入 `docs/screenshots/` 后替换下方路径即可。

<!--
| 管理端数据看板 | 会员端首页 |
| :---: | :---: |
| ![Dashboard](docs/screenshots/admin-dashboard.png) | ![Home](docs/screenshots/member-home.png) |
-->

## 🛠 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.11 · Django 5.0 · Django REST Framework 3.15 · SimpleJWT · drf-spectacular |
| 前端 | Vue 3 · Vite 8 · Element Plus · Pinia · Axios · ECharts · NProgress |
| 数据库 | MySQL 8.4 |
| 缓存 | Redis（django-redis，可选扩展） |
| 接口文档 | Swagger UI（drf-spectacular 自动生成） |

## 📁 目录结构

```text
.
├── backend/                        # Django 后端
│   ├── manage.py                   # Django 入口
│   ├── requirements.txt            # 后端依赖
│   ├── config/                     # 配置与路由
│   │   ├── settings/               # base.py / dev.py
│   │   ├── urls.py                 # 根路由 + Swagger
│   │   └── api_urls.py             # API 路由聚合
│   └── apps/
│       ├── users/                  # 用户、角色、认证
│       ├── venues/                 # 场馆、场地、时段
│       ├── bookings/               # 预约订单 + 冲突检测
│       ├── payments/               # 充值、消费、退款
│       ├── stats/                  # 数据统计
│       └── announcements/          # 系统公告
├── frontend/                       # Vue 3 前端
│   ├── vite.config.js              # @ 别名、/api 代理
│   ├── package.json
│   └── src/
│       ├── api/                    # 接口封装
│       ├── layouts/                # 布局（管理端 / 会员端）
│       ├── router/                 # 路由
│       ├── store/                  # Pinia 状态
│       ├── utils/                  # axios 拦截器、工具
│       └── views/
│           ├── admin/              # 管理端页面
│           ├── reception/          # 前台操作台
│           ├── member/             # 会员端页面
│           ├── Login.vue
│           ├── Register.vue
│           └── NotFound.vue
└── docs/                           # 项目文档（功能导图等）
```

## 🚀 快速开始

### 环境要求

- **Python** 3.10+（开发环境 3.11）
- **Node.js** 20+（开发环境 24）
- **MySQL** 8.x
- （可选）**Redis**

### 1. 配置数据库

创建数据库并修改 `backend/config/settings/base.py` 中的数据库配置（默认 `badminton_venue` / `root` / `123456` / `3306`）：

```sql
CREATE DATABASE badminton_venue CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

> 无 MySQL 时也可使用 `base.py` 中已注释的 SQLite 兜底配置。

### 2. 启动后端

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate     macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

接口文档（Swagger）：<http://localhost:8000/api/docs/>

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端开发服务器运行在 <http://localhost:3000>，并代理 `/api` 到后端 `http://localhost:8000`。

## 🔑 测试账号

| 角色 | 手机号 | 密码 | 入口 |
|------|--------|------|------|
| 管理员 | `13800000000` | `admin123` | `/admin/dashboard` |
| 前台 | `13900000001` | `123456` | `/admin/dashboard` |
| 会员 | `13800138001` | `123456` | `/` |

会员账号也可直接在前端注册页创建。

## 🗄 核心数据表

| 表 | 说明 |
|----|------|
| `users` | 用户、角色、会员等级、余额、黑名单状态 |
| `venues` | 场馆 |
| `courts` | 场地 |
| `time_slots` | 时段与价格 |
| `bookings` | 预约订单（原价、折扣率、实付金额、签到状态） |
| `payments` | 充值、消费、退款记录（含充值赠送） |
| `announcements` | 系统公告 |

## 🧭 主要接口

| 模块 | 接口示例 |
|------|----------|
| 认证 | `POST /api/auth/login/` · `POST /api/auth/register/` · `POST /api/auth/change-password/` |
| 用户 | `GET/POST /api/users/` · `GET/PATCH /api/users/me/` · `POST /api/users/{id}/blacklist/` |
| 场馆 | `GET/POST/PATCH/DELETE /api/venues/` · `/api/courts/` · `/api/time-slots/` |
| 预约 | `GET/POST /api/bookings/` · `GET /api/bookings/my/` · `POST /api/bookings/{id}/pay/` · `cancel/` · `check_in/` · `GET /api/bookings/export_csv/` |
| 支付 | `GET /api/payments/` · `POST /api/payments/recharge/` · `POST /api/payments/pay/` · `GET /api/payments/export_csv/` |
| 公告 | `GET/POST/PATCH/DELETE /api/announcements/` · `POST /api/announcements/{id}/toggle_publish/` |
| 统计 | `GET /api/stats/overview/` · `revenue_trend/` · `court_usage/` · `popular_slots/` |

> 完整交互式接口文档见 Swagger UI：<http://localhost:8000/api/docs/>

## 🔮 后续规划

- 优惠券 / 折扣券
- 教练陪练预约
- 场馆评价系统
- 短信 / 邮件通知

## 📄 License

本项目为毕业设计作品，仅用于学习交流。若需引用或二次开发，请保留原作者署名。
