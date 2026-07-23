<template>
  <div class="login-page">
    <el-card class="login-card">
      <h2>🏸 用户注册</h2>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="form.nickname" placeholder="请输入昵称（选填）" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="password2">
          <el-input v-model="form.password2" type="password" placeholder="请再次输入密码" show-password
            @keyup.enter="handleRegister" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" style="width:100%" :loading="loading" @click="handleRegister">注 册</el-button>
        </el-form-item>
        <el-form-item>
          <el-button link type="primary" @click="$router.push('/login')">已有账号？立即登录</el-button>
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

const router = useRouter()
const loading = ref(false)
const formRef = ref(null)

const form = reactive({ phone: '', nickname: '', password: '', password2: '' })

const validatePassword2 = (_rule, value, callback) => {
  if (value !== form.password) callback(new Error('两次密码不一致'))
  else callback()
}

const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1\d{10}$/, message: '手机号格式不正确', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' },
  ],
  password2: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validatePassword2, trigger: 'blur' },
  ],
}

async function handleRegister() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await api.post('auth/register/', {
        phone: form.phone,
        nickname: form.nickname,
        password: form.password,
        password2: form.password2,
      })
      ElMessage.success('注册成功，请登录')
      router.push('/login')
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
