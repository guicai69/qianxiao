# 羽毛球馆管理系统

> 毕业设计项目，基于 Django REST Framework 和 Vue 3 实现的多场馆、多场地、多时段预约管理系统。

## 项目状态

项目已完成主要业务闭环，当前处于联调与完善阶段。

| 模块 | 状态 |
|------|------|
| 项目初始化、前后端工程搭建 | 已完成 |
| 用户、角色、JWT 登录 | 已完成 |
| 场馆、场地、时段与定价管理 | 已完成 |
| 预约、冲突检测、订单管理 | 已完成 |
| 模拟支付、余额充值、退款 | 已完成 |
| 数据看板与前台操作台 | 已完成 |
| 会员等级与折扣 | 已完成 |
| 前后端联调、回归测试 | 已完成 |
| 论文、答辩材料与最终文档 | 待完成 |

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python / Django / Django REST Framework |
| 前端 | Vue 3 / Vite / Element Plus / Pinia / Axios |
| 数据库 | MySQL |
| 认证 | SimpleJWT |
| 可视化 | ECharts |
| 可选缓存 | Redis，用于后续热点缓存和接口限流扩展 |

## 用户与权限

系统包含三类角色：

- 管理员：用户管理、场馆场地管理、预约管理、支付记录、数据看板。
- 前台：操作台、场馆场地管理、预约管理、支付记录。
- 会员：场馆浏览、在线预约、余额充值、订单支付、个人中心。

会员等级与折扣：

| 等级 | 折扣 |
|------|------|
| 普通会员 `normal` | 原价 100% |
| 银卡会员 `silver` | 95 折 |
| 金卡会员 `gold` | 90 折 |

折扣在创建预约时写入订单快照，后续会员等级变化不会影响已生成订单。

## 功能概览

### 场馆、场地与时段

- 场馆 CRUD。
- 场地 CRUD，并支持按场馆查看。
- 时段 CRUD，支持不同时段独立定价。
- 已填充广州地区 5 个场馆示例数据。

### 预约与订单

- 会员按日期、场馆、场地、时段预约。
- 同一场地同一日期同一时段自动检测冲突。
- 预约创建后弹出支付窗口，或跳转到订单页面继续支付。
- 待支付订单可由会员自行取消。
- 已支付订单需由管理员或前台确认取消。
- 管理员取消已支付订单时自动将实际支付金额退回用户余额，并生成退款记录。

### 支付与余额

- 支持余额、微信、支付宝三种模拟支付方式。
- 支持会员余额充值。
- 充值赠送：充 100 送 10、充 300 送 40、充 500 送 80、充 1000 送 200。
- 消费累计自动升级会员等级（累计消费满 500 升银卡、满 2000 升金卡，只升不降）。
- 管理端支付记录展示用户手机号、昵称、类型、金额、赠送、支付方式、关联订单。
- 支付类型包括：充值、消费、退款。

### 公告、签到与数据导出

- 系统公告：管理端发布/置顶/下线，会员端首页展示。
- 到店签到核销：已支付订单由管理员/前台签到核销，会员端查看签到状态。
- 数据导出：预约订单、支付记录支持一键导出 CSV（Excel 可直接打开）。

### 数据统计

- 今日预约数、待处理数、今日营收、累计营收等总览指标。
- 各场馆场地数统计。
- 场馆启用状态统计。
- 前台操作台每 5 秒自动刷新，页面重新可见时也会立即同步。

### 前端界面

界面已按 Material Dashboard 风格优化：

- 管理端使用白色侧边栏、卡片化数据面板和现代顶部栏。
- 会员端使用顶部导航、卡片式场馆列表和预约流程。
- 登录、注册、数据看板、场馆详情、订单支付等页面已完成视觉统一。
- 全局路由切换使用 NProgress 顶部进度条（贴合主题主色）。
- 数据看板新增近 7 日营收趋势（折线+柱状）与热门时段（横向柱状）图表。
- 前台操作台每 5 秒自动刷新、页面重新可见时立即同步，并展示今日预约列表与营收趋势。
- 404 页面已按主题重绘，支付记录展示关联订单的场地/日期/时段。

## 目录结构

```text
E:\毕设\代码\
├── backend/                 # Django 后端
│   ├── config/              # 配置与路由
│   ├── apps/
│   │   ├── users/           # 用户、角色、认证
│   │   ├── venues/          # 场馆、场地、时段
│   │   ├── bookings/        # 预约订单
│   │   ├── payments/        # 充值、消费、退款
│   │   ├── stats/           # 数据统计
│   │   └── announcements/   # 系统公告
│   └── manage.py
├── frontend/                # Vue 3 前端
│   └── src/
│       ├── api/
│       ├── layouts/
│       ├── router/
│       ├── store/
│       ├── utils/
│       └── views/
├── docs/                    # 项目文档
├── admin-template/          # 参考模板，不参与运行
└── frontend-backup/         # 前端备份，不参与运行
```

## 核心数据表

| 表 | 说明 |
|----|------|
| `users` | 用户、角色、会员等级、余额、黑名单状态 |
| `venues` | 场馆 |
| `courts` | 场地 |
| `time_slots` | 时段与价格 |
| `bookings` | 预约订单，包含原价、折扣率、实付金额、签到状态 |
| `payments` | 充值、消费、退款记录（含充值赠送金额） |
| `announcements` | 系统公告 |

## API 概要

```text
POST /api/auth/login/
POST /api/auth/register/
POST /api/auth/change-password/

GET/POST /api/users/
GET/PATCH /api/users/me/
POST /api/users/{id}/blacklist/
POST /api/users/{id}/unblacklist/

GET/POST/PATCH/DELETE /api/venues/
GET/POST/PATCH/DELETE /api/courts/
GET/POST/PATCH/DELETE /api/time-slots/

GET/POST /api/bookings/
GET /api/bookings/my/
POST /api/bookings/{id}/cancel/
POST /api/bookings/{id}/pay/
POST /api/bookings/{id}/check_in/
GET /api/bookings/export_csv/

GET /api/payments/
POST /api/payments/recharge/
POST /api/payments/pay/
GET /api/payments/export_csv/

GET/POST/PATCH/DELETE /api/announcements/
POST /api/announcements/{id}/toggle_publish/
POST /api/announcements/{id}/toggle_pin/

GET /api/stats/overview/
GET /api/stats/revenue_trend/
GET /api/stats/court_usage/
GET /api/stats/popular_slots/
```

## 开发与运行

### 后端

```bash
cd backend
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
npm run build
```

开发环境下前端默认地址为 `http://localhost:3000`，代理 `/api` 到后端 `http://localhost:8000`。

## 测试账号

| 角色 | 手机号 | 密码 |
|------|--------|------|
| 管理员 | `13800000000` | `admin123` |
| 前台 | `13900000001` | `123456` |
| 会员 | `13570417539` | 当前数据库测试账号，密码按测试环境设置 |

会员账号也可以直接通过前端注册页创建。

## 当前已知事项

- `admin-template/` 和 `frontend-backup/` 为参考模板和备份目录，不影响主项目运行。
- Redis 当前作为可选扩展，不影响 MySQL 和前后端基本运行。
- 优惠券/折扣券、教练陪练预约、场馆评价等可作为后续扩展项。
- 2026-08 联调已补齐缺失迁移：`bookings.0002`（订单原价/折扣率字段）与 `users.0004`（会员等级补充银卡），并修复支付列表关联订单字段序列化。
