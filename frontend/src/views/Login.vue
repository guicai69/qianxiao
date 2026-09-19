<template>
  <AuthShell>
    <h1 class="auth-title">欢迎回来</h1>
    <p class="auth-sub">登录后查看场馆、场地与可预约时段</p>

    <el-form ref="formRef" :model="form" :rules="rules" size="large" class="auth-form" @submit.prevent>
      <el-form-item prop="phone">
        <el-input
          v-model="form.phone"
          placeholder="手机号"
          :prefix-icon="Iphone"
          autocomplete="username"
        />
      </el-form-item>
      <el-form-item prop="password">
        <el-input
          v-model="form.password"
          type="password"
          placeholder="密码"
          :prefix-icon="Lock"
          show-password
          autocomplete="current-password"
          @keyup.enter="handleLogin"
        />
      </el-form-item>

      <el-button type="primary" class="submit-button" :loading="loading" @click="handleLogin">
        登录
        <el-icon class="el-icon--right"><ArrowRight /></el-icon>
      </el-button>
    </el-form>

    <div class="auth-switch">
      <span>还没有账号？</span>
      <el-button link type="primary" @click="$router.push('/register')">立即注册</el-button>
    </div>

    <!-- 演示用：答辩现场点一下就把账号填好，不用背手机号 -->
    <div class="demo-hint">
      <div class="demo-head">
        <span class="caps">演示账号 · 点击填充</span>
      </div>
      <button
        v-for="a in demoAccounts"
        :key="a.phone"
        type="button"
        class="demo-account"
        @click="fill(a)"
      >
        <span class="demo-role">{{ a.role }}</span>
        <span class="demo-cred mono">{{ a.phone }} / {{ a.password }}</span>
      </button>
    </div>
  </AuthShell>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Iphone, Lock, ArrowRight } from '@element-plus/icons-vue'
import api from '@/api'
import { useUserStore } from '@/store'
import AuthShell from '@/components/brand/AuthShell.vue'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const formRef = ref(null)

const form = reactive({ phone: '', password: '' })

const demoAccounts = [
  { role: '管理员', phone: '13800000000', password: 'admin123' },
  { role: '前台', phone: '13900000001', password: '123456' },
]

function fill(a) {
  form.phone = a.phone
  form.password = a.password
}

const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1\d{10}$/, message: '手机号格式不正确', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' },
  ],
}

async function handleLogin() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      const res = await api.post('auth/login/', { phone: form.phone, password: form.password })
      const { access, refresh, user } = res.data
      userStore.setToken(access, refresh)
      userStore.setUserInfo(user)
      ElMessage.success('登录成功')
      if (user.role === 'admin') router.push('/admin/dashboard')
      else if (user.role === 'reception') router.push('/reception/dashboard')
      else router.push('/')
    } catch {
      // 错误已由拦截器统一提示
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.auth-title {
  margin: 0 0 8px;
  font-size: var(--fs-28);
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--ink-1);
}

.auth-sub {
  margin: 0 0 28px;
  font-size: var(--fs-13);
  line-height: var(--lh-body);
  color: var(--ink-3);
}

.auth-form :deep(.el-form-item) {
  margin-bottom: 18px;
}

.submit-button {
  width: 100%;
  height: 46px;
  margin-top: 4px;
  font-size: var(--fs-14);
}

.auth-switch {
  display: flex;
  align-items: center;
  gap: 4px;
  justify-content: center;
  margin-top: 18px;
  font-size: var(--fs-13);
  color: var(--ink-3);
}

.demo-hint {
  margin-top: 30px;
  padding: 14px 16px 8px;
  border: 1px dashed var(--border-strong);
  border-radius: var(--radius);
  background: var(--surface);
}

.demo-head {
  margin-bottom: 8px;
}

.demo-account {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
  padding: 8px 6px;
  border: 0;
  border-top: 1px solid var(--border-soft);
  background: none;
  cursor: pointer;
  text-align: left;
  transition: background-color var(--dur-2) var(--ease-out);
}

.demo-account:hover {
  background: var(--accent-soft);
}

.demo-role {
  font-size: var(--fs-13);
  font-weight: 700;
  color: var(--ink-1);
}

.demo-cred {
  font-size: var(--fs-12);
  color: var(--ink-3);
}
</style>
