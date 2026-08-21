<template>
  <div class="auth-shell">
    <section class="auth-visual">
      <div class="visual-content">
        <span class="visual-icon"><el-icon :size="32"><Medal /></el-icon></span>
        <h1>羽毛球馆预约</h1>
        <p>创建账号，开始预约场馆</p>
      </div>
    </section>

    <section class="auth-form-wrap">
      <div class="auth-card">
        <div class="auth-heading">
          <h2>创建账号</h2>
          <p>注册后即可预约场地并管理订单</p>
        </div>

        <el-form ref="formRef" :model="form" :rules="rules" size="large" @submit.prevent>
          <el-form-item prop="phone">
            <el-input v-model="form.phone" placeholder="手机号" :prefix-icon="Iphone" />
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
            />
          </el-form-item>
          <el-form-item prop="password2">
            <el-input
              v-model="form.password2"
              type="password"
              placeholder="确认密码"
              :prefix-icon="Lock"
              show-password
              @keyup.enter="handleRegister"
            />
          </el-form-item>
          <el-button
            type="primary"
            class="submit-button"
            :loading="loading"
            @click="handleRegister"
          >
            注册
            <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>
        </el-form>

        <div class="auth-switch">
          <span>已有账号？</span>
          <el-button link type="primary" @click="$router.push('/login')">立即登录</el-button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue"
import { useRouter } from "vue-router"
import { ElMessage } from "element-plus"
import { Iphone, User, Lock, ArrowRight, Medal } from "@element-plus/icons-vue"
import api from "@/api"

const router = useRouter()
const loading = ref(false)
const formRef = ref(null)

const form = reactive({ phone: "", nickname: "", password: "", password2: "" })

const validatePassword2 = (_rule, value, callback) => {
  if (value !== form.password) callback(new Error("两次密码不一致"))
  else callback()
}

const rules = {
  phone: [
    { required: true, message: "请输入手机号", trigger: "blur" },
    { pattern: /^1\d{10}$/, message: "手机号格式不正确", trigger: "blur" },
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, message: "密码至少6位", trigger: "blur" },
  ],
  password2: [
    { required: true, message: "请再次输入密码", trigger: "blur" },
    { validator: validatePassword2, trigger: "blur" },
  ],
}

async function handleRegister() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await api.post("auth/register/", {
        phone: form.phone,
        nickname: form.nickname,
        password: form.password,
        password2: form.password2,
      })
      ElMessage.success("注册成功，请登录")
      router.push("/login")
    } catch {
      // error handled by interceptor
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.auth-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(420px, 560px);
  background: var(--mui-surface);
}

.auth-visual {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px;
  color: #ffffff;
  background:
    linear-gradient(rgba(15, 23, 42, 0.1), rgba(15, 23, 42, 0.12)),
    repeating-linear-gradient(
      135deg,
      rgba(255, 255, 255, 0.05) 0,
      rgba(255, 255, 255, 0.05) 1px,
      transparent 1px,
      transparent 18px
    ),
    #0f172a;
  overflow: hidden;
}

.visual-content {
  position: relative;
  z-index: 1;
  max-width: 460px;
}

.visual-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  margin-bottom: 28px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 18px;
  color: #ffffff;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(8px);
}

.visual-content h1 {
  margin: 0 0 12px;
  font-size: 38px;
  font-weight: 800;
  letter-spacing: 0;
}

.visual-content p {
  margin: 0;
  color: #cbd5e1;
  font-size: 16px;
}

.auth-form-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 32px;
}

.auth-card {
  width: 100%;
  max-width: 400px;
}

.auth-heading {
  margin-bottom: 32px;
}

.auth-heading h2 {
  margin: 0 0 8px;
  color: var(--mui-text);
  font-size: 30px;
  font-weight: 800;
}

.auth-heading p {
  margin: 0;
  color: var(--mui-muted);
  font-size: 14px;
}

.submit-button {
  width: 100%;
  height: 46px;
  margin-top: 8px;
  font-size: 15px;
}

.auth-switch {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: 24px;
  color: var(--mui-muted);
  font-size: 14px;
}

@media (max-width: 900px) {
  .auth-shell {
    grid-template-columns: 1fr;
  }

  .auth-visual {
    display: none;
  }
}
</style>
