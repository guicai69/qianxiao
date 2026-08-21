<template>
  <div class="login-page">
    <el-card class="login-card">
      <h2>🏸 羽毛球馆管理系统</h2>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password
            @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" style="width:100%" :loading="loading" @click="handleLogin">登 录</el-button>
        </el-form-item>
        <el-form-item>
          <el-button link type="primary" @click="$router.push('/register')">还没有账号？立即注册</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'
import { useUserStore } from '@/store'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const formRef = ref(null)

const form = reactive({ phone: '', password: '' })
const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1\d{10}$/, message: '手机号格式不正确', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' },
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
      // 按角色跳转
      if (user.role === 'admin') router.push('/admin/dashboard')
      else if (user.role === 'reception') router.push('/admin/dashboard')
      else router.push('/')
    } catch {
      // error handled by interceptor
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-page { display: flex; align-items: center; justify-content: center; height: 100vh; background: #f0f2f5; }
.login-card { width: 420px; }
.login-card h2 { text-align: center; margin-bottom: 24px; }
</style>
