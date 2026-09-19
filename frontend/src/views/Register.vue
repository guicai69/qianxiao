<template>
  <AuthShell>
    <h1 class="auth-title">创建会员账号</h1>
    <p class="auth-sub">注册后即可预约场地。累计消费满 ¥500 升银卡，满 ¥2000 升金卡。</p>

    <el-form ref="formRef" :model="form" :rules="rules" size="large" class="auth-form" @submit.prevent>
      <el-form-item prop="phone">
        <el-input v-model="form.phone" placeholder="手机号" :prefix-icon="Iphone" autocomplete="username" />
      </el-form-item>
      <el-form-item prop="nickname">
        <el-input v-model="form.nickname" placeholder="昵称（选填）" :prefix-icon="User" />
      </el-form-item>
      <el-form-item prop="password">
        <el-input
          v-model="form.password"
          type="password"
          placeholder="密码"
          :prefix-icon="Lock"
          show-password
          autocomplete="new-password"
        />
      </el-form-item>
      <el-form-item prop="password2">
        <el-input
          v-model="form.password2"
          type="password"
          placeholder="确认密码"
          :prefix-icon="Lock"
          show-password
          autocomplete="new-password"
          @keyup.enter="handleRegister"
        />
      </el-form-item>

      <el-button type="primary" class="submit-button" :loading="loading" @click="handleRegister">
        注册
        <el-icon class="el-icon--right"><ArrowRight /></el-icon>
      </el-button>
    </el-form>

    <div class="auth-switch">
      <span>已有账号？</span>
      <el-button link type="primary" @click="$router.push('/login')">立即登录</el-button>
    </div>
  </AuthShell>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Iphone, User, Lock, ArrowRight } from '@element-plus/icons-vue'
import api from '@/api'
import AuthShell from '@/components/brand/AuthShell.vue'

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
    { min: 6, message: '密码至少 6 位', trigger: 'blur' },
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
  margin: 0 0 26px;
  font-size: var(--fs-13);
  line-height: var(--lh-body);
  color: var(--ink-3);
}

.auth-form :deep(.el-form-item) {
  margin-bottom: 16px;
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
</style>
