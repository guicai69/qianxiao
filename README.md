# Badminton Venue Management System · 羽毛球馆管理系统

> 毕业设计 — 基于 Python 前后端分离的羽毛球馆管理系统

---

## 一、项目概述

面向羽毛球馆的日常运营管理系统，支持多场馆、多场地、多时段下的场地预约、会员管理及数据统计分析。系统分为三类用户角色：管理员、前台店员和会员，各自拥有不同的功能权限。

---

## 二、技术栈

| 层级 | 技术选型 |
|------|----------|
| **后端** | Python · Django + Django REST Framework |
| **前端** | Vue 3 + Element Plus（Node.js 生态） |
| **数据库** | MySQL |
| **认证** | JWT 无状态认证（djangorestframework-simplejwt） |
| **缓存** | Redis（JWT 黑名单 / 热点数据缓存 / 接口限流） |
| **API 文档** | DRF Browsable API / drf-spectacular (OpenAPI) |
| **数据可视化** | ECharts |

---

## 三、用户角色

| 角色 | 说明 | 核心职责 |
|------|------|----------|
| **管理员** | 系统超级用户 | 全局管理：场馆/场地/价格配置、所有用户管理、数据看板 |
| **前台店员** | 场馆运营人员 | 代客预约、现场收费、核销订单 |
| **会员** | C 端普通用户 | 注册登录、浏览场地时段、在线预约、模拟支付、查看消费记录 |

---

## 四、核心功能模块

### 4.1 场地预约管理（核心）

- **场馆管理**：支持多场馆（如「XX羽毛球馆A店」「XX羽毛球馆B店」），每个场馆独立配置
- **场地管理**：每个场馆下有多片场地（如 1 号场 ~ 6 号场）
- **时段管理**：每片场地按固定时段划分（如 9:00-10:00、10:00-11:00 …），支持不同时段差异化定价
- **预约流程**：会员选择场馆 → 选择日期 → 查看可用时段 → 提交预约 → 模拟支付 → 预约成功
- **冲突检测**：同一场地同一时段不可重复预约
- **取消预约**：支持在限定时间前取消（如提前 2 小时），超时不可取消
- **预约记录**：会员查看自己的预约历史；前台/管理员查看所管辖场馆的全部预约

### 4.2 会员 / 用户体系

- **注册登录**：手机号 + 密码注册，JWT Token 登录，支持 Token 刷新
- **三角色区分**：注册默认为会员角色；管理员/前台账号由管理员后台创建
- **个人中心**：查看/编辑个人信息、修改密码
- **会员等级**：普通会员 / 金卡会员 等，不同等级享受不同折扣
- **余额充值**：会员在线充值（模拟），前台也可代为充值
- **消费记录**：会员查看个人充值/消费明细

### 4.3 数据统计看板

- **营收统计**：按日/周/月统计各场馆营收，支持图表展示
- **场地使用率**：各场地、各时段的预约率分析
- **热门时段排行**：统计哪些时段最受欢迎，辅助定价决策
- **会员统计**：新增会员趋势、会员活跃度分析
- **可视化**：使用 ECharts 呈现柱状图、折线图、饼图等

### 4.4 模拟支付

- 预约提交后进入模拟支付页面
- 展示订单金额、支付方式选择（余额支付 / 模拟微信 / 模拟支付宝）
- 点击确认后模拟支付成功，订单状态更新为「已支付」
- 前台可在系统中标记线下已付款

---

## 五、非功能性需求

- **前后端分离**：前后端完全解耦，通过 RESTful API 通信
- **权限控制**：基于角色的访问控制（RBAC），不同角色看到不同菜单和功能
- **响应式布局**：前端适配 PC 端管理后台，会员端可兼顾移动端浏览器
- **数据校验**：前后端双重校验，保证数据合法性
- **安全**：JWT 过期刷新、敏感接口权限校验、SQL 防注入（Django ORM）
- **缓存**：Redis 缓存热点数据（场地可用时段、统计看板），JWT 黑名单防 Token 泄露

---

## 六、项目结构（规划）

```
E:\毕设\代码\
├── backend/                 # Django + DRF 后端
│   ├── manage.py
│   ├── config/              # Django 配置（settings, urls, wsgi）
│   │   ├── settings/
│   │   │   ├── base.py      # 公共配置
│   │   │   └── dev.py       # 开发环境配置
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── apps/                # Django 应用模块
│       ├── users/           # 用户 & 认证模块
│       ├── venues/          # 场馆 & 场地 & 时段模块
│       ├── bookings/        # 预约 & 订单模块
│       ├── payments/        # 支付 & 充值模块
│       └── stats/           # 数据统计模块
├── frontend/                # Vue 3 + Element Plus 前端
│   ├── src/
│   │   ├── api/             # axios 封装 & API 接口
│   │   ├── components/      # 公共组件
│   │   ├── layouts/         # 布局组件（管理端 / 会员端）
│   │   ├── router/          # 路由配置 + 权限守卫
│   │   ├── store/           # Pinia 状态管理
│   │   ├── utils/           # 工具函数
│   │   └── views/           # 页面视图
│   │       ├── admin/       # 管理员端页面
│   │       ├── reception/   # 前台端页面
│   │       └── member/      # 会员端页面
│   └── package.json
└── docs/                    # 文档（ER图、API文档、答辩PPT等）
```

---

## 七、数据库核心表设计（预览）

| 表名 | 说明 | 关键字段 |
|------|------|----------|
| `users` | 用户表 | id, phone, password, role(admin/reception/member), level, balance |
| `venues` | 场馆表 | id, name, address, phone, status |
| `courts` | 场地表 | id, venue_id(FK), name, status |
| `time_slots` | 时段表 | id, start_time, end_time, price |
| `bookings` | 预约订单表 | id, user_id(FK), court_id(FK), date, time_slot_id(FK), status, amount |
| `payments` | 支付记录表 | id, booking_id(FK), user_id(FK), type(recharge/booking), amount, method, status |
| `recharges` | 充值记录表 | id, user_id(FK), amount, method, operator_id(FK) |

---

## 八、开发计划

- [ ] 阶段一：项目初始化 — 后端 Django 项目搭建、前端 Vue 项目搭建、MySQL 数据库建库  🔧 `init` `db-schema` `django-model`
- [ ] 阶段二：用户模块 — 注册/登录/JWT 认证、角色管理、个人信息 CRUD  🔧 `django-model` `drf-api` `vue-crud` `review` `security-review` `test`
- [ ] 阶段三：场馆场地模块 — 场馆/场地/时段的增删改查、定价配置  🔧 `django-model` `drf-api` `vue-crud` `review`
- [ ] 阶段四：预约模块 — 预约流程、冲突检测、取消、订单管理  🔧 `drf-api` `explore` `review` `test`
- [ ] 阶段五：支付模块 — 模拟支付、余额充值、消费记录  🔧 `drf-api` `vue-crud` `security-review` `test`
- [ ] 阶段六：统计看板 — 营收/使用率/热门时段统计、ECharts 可视化  🔧 `research` `explore` `drf-api` `vue-crud` `review`
- [ ] 阶段七：联调 & 测试 — 前后端联调、Bug 修复、功能完善  🔧 `test` `review` `security-review`
- [ ] 阶段八：文档 & 答辩 — 撰写论文、整理答辩材料  🔧 `init` `review`
