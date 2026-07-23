---
name: vue-crud
description: Element Plus 表格/表单/分页 CRUD 页面模板 — 本项目前端标准
---

# vue-crud — Element Plus CRUD 页面模板

本项目使用 Vue 3 + Element Plus，CRUD 页面遵循以下标准结构。

## 页面文件结构

```
src/views/<module>/
├── index.vue          # 列表页（搜索 + 表格 + 分页）
├── components/
│   ├── FormDialog.vue # 新增/编辑弹窗
│   └── DetailDrawer.vue # 详情抽屉（按需）
```

## API 封装（src/api/）

```typescript
// src/api/request.ts — axios 实例
import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// 请求拦截：附加 JWT Token
request.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 响应拦截：统一错误处理 + Token 刷新
request.interceptors.response.use(
  res => res.data,
  async err => {
    if (err.response?.status === 401) {
      // Token 过期，尝试刷新
      const refresh = localStorage.getItem('refresh_token')
      if (refresh) {
        try {
          const { data } = await axios.post('/api/auth/refresh/', { refresh })
          localStorage.setItem('access_token', data.access)
          err.config.headers.Authorization = `Bearer ${data.access}`
          return request(err.config)
        } catch {
          localStorage.clear()
          router.push('/login')
        }
      }
    }
    ElMessage.error(err.response?.data?.message || '请求失败')
    return Promise.reject(err)
  }
)

export default request
```

```typescript
// src/api/bookings.ts — 模块 API
import request from './request'

export interface Booking {
  id: number
  court_name: string
  date: string
  time_slot_display: string
  status: string
  amount: number
  created_at: string
}

export const bookingApi = {
  list(params: object) {
    return request.get<{ results: Booking[]; count: number }>('/bookings/', { params })
  },
  create(data: object) {
    return request.post<Booking>('/bookings/', data)
  },
  detail(id: number) {
    return request.get<Booking>(`/bookings/${id}/`)
  },
  cancel(id: number) {
    return request.post(`/bookings/${id}/cancel/`)
  },
}
```

## 列表页模板（index.vue）

```vue
<template>
  <div class="page-container">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :model="query" inline>
        <el-form-item label="日期">
          <el-date-picker v-model="query.date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.status" clearable placeholder="全部">
            <el-option label="待支付" value="pending" />
            <el-option label="已支付" value="paid" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">搜索</el-button>
          <el-button @click="query = {}; fetchData()">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 表格 -->
    <el-card>
      <el-button type="primary" @click="handleAdd" v-if="hasPerm('add')">新增预约</el-button>
      <el-table :data="list" border stripe v-loading="loading">
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column prop="court_name" label="场地" />
        <el-table-column prop="date" label="日期" />
        <el-table-column prop="time_slot_display" label="时段" />
        <el-table-column prop="amount" label="金额" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="handleDetail(row)">详情</el-button>
            <el-button size="small" type="danger" @click="handleCancel(row)"
              v-if="row.status === 'pending' && hasPerm('cancel')">取消</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :total="total"
        layout="total, prev, pager, next"
        @change="fetchData"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { bookingApi, type Booking } from '@/api/bookings'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()
const list = ref<Booking[]>([])
const total = ref(0)
const loading = ref(false)

const query = reactive({
  page: 1,
  page_size: 20,
  date: '',
  status: '',
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await bookingApi.list(query)
    list.value = res.results
    total.value = res.count
  } finally {
    loading.value = false
  }
}

const statusTag = (s: string) => ({ pending: 'warning', paid: 'success', cancelled: 'info' }[s])
const statusLabel = (s: string) => ({ pending: '待支付', paid: '已支付', cancelled: '已取消' }[s])

const hasPerm = (action: string) => userStore.hasPermission(action)

const handleCancel = async (row: Booking) => {
  await ElMessageBox.confirm('确定要取消该预约吗？', '提示', { type: 'warning' })
  await bookingApi.cancel(row.id)
  ElMessage.success('已取消')
  fetchData()
}

onMounted(fetchData)
</script>
```

## 权限指令（v-permission）

```typescript
// src/directives/permission.ts
import type { Directive } from 'vue'
import { useUserStore } from '@/store/user'

export const permission: Directive = {
  mounted(el, binding) {
    const { hasPermission } = useUserStore()
    if (!hasPermission(binding.value)) {
      el.parentNode?.removeChild(el)
    }
  },
}
```

## 路由守卫

```typescript
// src/router/index.ts
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) {
    return next('/login')
  }
  if (to.meta.roles) {
    const userStore = useUserStore()
    if (!to.meta.roles.includes(userStore.role)) {
      return next('/403')
    }
  }
  next()
})
```

## Element Plus 常用组件速查

| 场景 | 组件 |
|------|------|
| 表格 | `el-table` + `el-table-column` |
| 分页 | `el-pagination` |
| 表单 | `el-form` + `el-form-item` |
| 弹窗 | `el-dialog` |
| 抽屉 | `el-drawer` |
| 搜索 | `el-input` / `el-select` / `el-date-picker` |
| 状态标签 | `el-tag` |
| 确认框 | `ElMessageBox.confirm` |
| 消息提示 | `ElMessage.success/error/warning` |
| 图标 | `@element-plus/icons-vue` |
