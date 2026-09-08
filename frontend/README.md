# frontend — Vue 3 前端

羽毛球馆管理系统的前端，基于 **Vue 3 + Vite + Element Plus** 构建。

## 技术栈

- Vue 3（Composition API）· Vite 8 · Element Plus · Pinia · Axios · ECharts · NProgress

## 目录结构

```text
frontend/
├── vite.config.js              # @ 别名、/api 代理到 :8000
├── package.json
└── src/
    ├── main.js                 # 入口（Element Plus / 中文 locale / Pinia / Router）
    ├── api/                    # 接口封装
    ├── layouts/                # AdminLayout / MemberLayout
    ├── router/                 # 路由与守卫
    ├── store/                  # Pinia（token / 用户信息）
    ├── utils/                  # axios 拦截器、导出、充值工具
    └── views/
        ├── admin/              # 管理端页面（看板 / 用户 / 场馆 / 场地 / 时段 / 预约 / 支付 / 公告）
        ├── reception/          # 前台操作台
        ├── member/             # 会员端页面（首页 / 场馆 / 预约 / 订单 / 个人中心）
        ├── Login.vue
        ├── Register.vue
        └── NotFound.vue
```

## 启动

```bash
cd frontend
npm install
npm run dev       # 开发服务器 :3000，代理 /api → :8000
npm run build     # 生产构建 → dist/
```
