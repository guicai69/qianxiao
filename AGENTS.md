# 羽毛球馆管理系统 — Badminton Venue Management

毕业设计 · Django + DRF 后端 · Vue 3 + Element Plus 前端 · MySQL 8.4

## Project

- **后端** `backend/` — Django 4.2 + DRF + SimpleJWT + drf-spectacular
- **前端** `frontend/` — Vue 3 (Composition API) + Vite 8 + Element Plus + Pinia + Axios + ECharts
- **缓存** Redis + django-redis — JWT 黑名单、场地可用时段缓存、统计缓存
- **数据库** MySQL 8.4, 端口 3306, 库名 `badminton_venue`, root/123456
- **缓存** Redis, 端口 6379, django-redis (JWT 黑名单 / 热点缓存 / 限流)
- **入口** 后端 `backend/manage.py` runserver 0.0.0.0:8000; 前端 `npm run dev` → :3000 → proxy `/api` → :8000

## Commands

```bash
# 后端
cd backend
python manage.py check                    # 配置检查
python manage.py makemigrations           # 生成迁移
python manage.py migrate                  # 执行迁移
python manage.py runserver 0.0.0.0:8000   # 启动服务
python manage.py shell                    # Django shell

# 前端
cd frontend
npm run dev     # 开发服务器 :3000
npm run build   # 生产构建 → dist/
npm run preview # 预览构建产物

# MySQL (Windows)
# 服务名 MySQL84, 数据目录 C:\Users\17507\mysql84data
net start MySQL84
net stop MySQL84

# Redis (Windows — Memurai 或 WSL2)
redis-server                                          # 前台启动
redis-server --service-start                          # 服务模式（Memurai）
wsl -d Ubuntu -- sudo service redis-server start      # WSL2 方式
```

## Architecture

```
backend/
├── manage.py                        # Django 入口
├── config/
│   ├── settings/base.py             # 公共配置（DB/JWT/CORS/DRF）
│   ├── settings/dev.py              # 开发覆写
│   ├── urls.py                      # 根路由 + Swagger (/api/docs/)
│   └── api_urls.py                  # API 路由聚合（各 app router 在此注册）
├── apps/
│   ├── users/                       # 用户认证 — AbstractUser (phone/login/role/balance)
│   ├── venues/                      # 场馆/场地/时段管理
│   ├── bookings/                    # 预约订单 + 冲突检测
│   ├── payments/                    # 模拟支付 + 充值
│   └── stats/                       # 数据统计 + ECharts
└── requirements.txt

frontend/src/
├── main.js                          # 入口：注册 ElementPlus/中文/Pinia/Router/图标
├── api/index.js                     # axios 封装 + 基础 API
├── router/index.js                  # 路由：/admin /reception / /login
├── store/index.js                   # Pinia: useUserStore (token/refreshToken/userInfo)
├── utils/request.js                 # axios 拦截器：JWT 附加 + 401/403/500 统一处理
├── layouts/
│   ├── AdminLayout.vue              # 侧边栏布局（管理端/前台共用）
│   └── MemberLayout.vue             # 顶部导航布局（会员端）
├── views/
│   ├── admin/Dashboard.vue          # 管理后台首页
│   ├── reception/Dashboard.vue      # 前台操作台
│   ├── member/Home.vue              # 会员首页
│   ├── Login.vue                    # 登录页
│   └── NotFound.vue                 # 404
└── vite.config.js                   # @ 别名 → src/, proxy /api → :8000
```

## Conventions

- **Django app**: 全在 `apps/` 下，AppConfig.name = `apps.<name>`，verbose_name 中文
- **User model**: `AUTH_USER_MODEL = 'users.User'`，继承 AbstractUser
- **DRF**: 每个 app 三 Serializer（List/Detail/Create），ViewSet 用 `get_serializer_class` 按 action 切换
- **Router**: 每个 app 的 `urls.py` 用 DefaultRouter 注册，汇总到 `config/api_urls.py`
- **权限**: 默认 IsAuthenticated，按角色用自定义 BasePermission（IsOwnerOrStaff / IsAdminOrReception）
- **金额**: DecimalField(max_digits=10, decimal_places=2)，不用 FloatField
- **choices**: 常量定义在 Model 顶部，格式 `STATUS_XXX = 'xxx'`
- **级联**: 用户 → CASCADE；场地/时段 → PROTECT（有预约不可删）
- **前端路径**: `@/` 别名指向 `src/`，所有 import 使用 `@/`
- **Pinia**: Composition API store（`defineStore` + `ref`）
- **中文**: settings LANGUAGE_CODE = zh-hans, TIME_ZONE = Asia/Shanghai, Element Plus 中文 locale

## Skills (project)

加载本项目 `.reasonix/skills/` 下的规范模板：
- `db-schema` — MySQL 建表/索引/迁移检查
- `django-model` — Model 字段/Meta/外键/choices 规范
- `drf-api` — Serializer + ViewSet + Router 模板
- `vue-crud` — Element Plus 表格/表单/分页 CRUD 模板

## Notes

- 开发阶段 MySQL 8.4 通过 Windows 服务 MySQL84 管理；若服务不可用，可用 SQLite 兜底（base.py 中已注释）
- 阶段一已完成：项目骨架 + 自定义 User 迁移 + 前后端可构建
- 阶段二已完成：用户模块（注册/登录/JWT 认证/角色管理/权限体系）
- 阶段三已完成：场馆场地模块（Venue/Court/TimeSlot CRUD + 定价配置 + 前端管理页面）
- 已填充广州5个场馆数据（天河6场/海珠5场/白云4场/番禺4场/越秀5场）+ 各14个时段 ¥30-120
- 前端模板 vue-element-plus-admin (29k星) 已下载至 admin-template/ 供参考

### 当前运行服务

| 服务 | 端口 | 命令 |
|------|------|------|
| Django API | :8000 | cd backend && python manage.py runserver 0.0.0.0:8000 |
| 前端 Dev Server | :3000 | cd frontend && npm run dev |

### 测试账号

| 角色 | 手机号 | 密码 | 入口 |
|------|--------|------|------|
| 管理员 | 13800000000 | admin123 | /admin/dashboard |
| 前台 | 13900000001 | 123456 | /admin/dashboard |
| 会员 | 13800138001 | 123456 | / |

## Agent skills

### Issue tracker

Issues are tracked as GitHub issues in `guicai69/qianxiao`, using the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Domain docs

Single-context: one `CONTEXT.md` at the repo root plus `docs/adr/`. See `docs/agents/domain.md`.
