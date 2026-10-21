<template>
  <AuthShell>
    <!-- 门面换幕：左半深蓝球馆面上叠三团极光，只在视觉区，表单纸面不受影响 -->
    <div class="auth-aurora" data-plane="deep" aria-hidden="true">
      <span class="fx-aurora__blob"></span>
      <span class="fx-aurora__blob fx-aurora__blob--b"></span>
      <span class="fx-aurora__blob fx-aurora__blob--c"></span>
    </div>

    <h1 class="auth-title fx-rise fx-ink-gradient">欢迎回来</h1>
    <span class="auth-rule" aria-hidden="true"></span>
    <p class="auth-sub fx-rise">登录后查看场馆、场地与可预约时段</p>

    <el-form ref="formRef" :model="form" :rules="rules" size="large" class="auth-form fx-rise" @submit.prevent>
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
        />
      </el-form-item>
      <el-form-item prop="captchaCode">
        <div class="captcha-row">
          <el-input
            v-model="form.captchaCode"
            placeholder="验证码"
            maxlength="4"
            @keyup.enter="handleLogin"
          />
          <button type="button" class="captcha-img fx-press" aria-label="点击刷新验证码" @click="fetchCaptcha">
            <span v-if="captchaSvg" v-html="captchaSvg"></span>
            <span v-else class="captcha-loading mono">点击获取</span>
          </button>
        </div>
      </el-form-item>

      <el-button type="primary" class="submit-button fx-border-glow fx-press" :loading="loading" @click="handleLogin">
        登录
        <el-icon class="el-icon--right"><ArrowRight /></el-icon>
      </el-button>
    </el-form>

    <div class="auth-switch fx-rise">
      <span>还没有账号？</span>
      <el-button link type="primary" @click="$router.push('/register')">立即注册</el-button>
    </div>

    <!-- 演示用：答辩现场点一下就把账号填好，不用背手机号 -->
    <div class="demo-hint fx-rise">
      <div class="demo-head">
        <span class="caps">演示账号 · 点击填充（验证码看图手动输入）</span>
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
import { reactive, ref, onMounted } from 'vue'
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
const captchaSvg = ref('')

const form = reactive({ phone: '', password: '', captchaId: '', captchaCode: '' })

async function fetchCaptcha() {
  try {
    const res = await api.get('auth/captcha/')
    form.captchaId = res.data.captcha_id
    captchaSvg.value = res.data.svg
    form.captchaCode = ''
  } catch {
    // 错误已由拦截器统一提示
  }
}

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
  captchaCode: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
  ],
}

async function handleLogin() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      const res = await api.post('auth/login/', {
        phone: form.phone,
        password: form.password,
        captcha_id: form.captchaId,
        captcha_code: form.captchaCode,
      })
      const { access, refresh, user } = res.data
      userStore.setToken(access, refresh)
      userStore.setUserInfo(user)
      ElMessage.success('登录成功')
      if (user.role === 'admin') router.push('/admin/dashboard')
      else if (user.role === 'reception') router.push('/reception/dashboard')
      else router.push('/')
    } catch {
      // 错误已由拦截器统一提示；验证码失败后刷新一张新的
      fetchCaptcha()
    } finally {
      loading.value = false
    }
  })
}

onMounted(fetchCaptcha)
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

.captcha-row {
  display: flex;
  gap: 8px;
  width: 100%;
}

.captcha-row :deep(.el-input) {
  flex: 1;
}

.captcha-img {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 120px;
  height: 40px;
  padding: 0;
  border: 1px solid var(--border);
  border-radius: var(--radius-xs);
  background: var(--sunken);
  cursor: pointer;
  overflow: hidden;
}

.captcha-img :deep(svg) {
  display: block;
}

.captcha-loading {
  font-size: var(--fs-12);
  color: var(--ink-3);
}

/* ==========================================================================
   动效（2026-10）：换幕、入场节拍、聚焦光晕、主按钮描边
   装饰层在 reduce 下整个撤掉，进场元素停在终态
   ========================================================================== */

/* 左半深色面的三团极光：右边界对齐 AuthShell 的 520px 表单栏，
   screen 混合只加光不加灰；右侧用蒙版收住，别漫到纸面表单上 */
.auth-aurora {
  position: fixed;
  inset: 0 520px 0 0;
  z-index: 0;
  overflow: hidden;
  opacity: 0.8;
  pointer-events: none;
  background: transparent;
  mix-blend-mode: screen;
  -webkit-mask-image: linear-gradient(90deg, #000 58%, transparent 94%);
  mask-image: linear-gradient(90deg, #000 58%, transparent 94%);
}

/* 工具箱里 --b / --c 只写了单侧偏移，另一侧仍继承基类的 left/top，
   这里把该归零的那侧补上，其余仍用工具箱定义 */
.auth-aurora .fx-aurora__blob--b {
  left: auto;
}

.auth-aurora .fx-aurora__blob--c {
  top: auto;
}

@media (max-width: 980px), (prefers-reduced-motion: reduce) {
  .auth-aurora {
    display: none;
  }
}

/* 标题渐变墨：让渐变贴着文字走，而不是铺满整行 */
.auth-title {
  width: fit-content;
}

/* 首屏入场节拍：70ms 一步，与 .fx-rise 同一套刻度 */
.auth-title { --i: 0; }
.auth-sub { --i: 1; }
.auth-form { --i: 2; }
.auth-switch { --i: 3; }
.demo-hint { --i: 4; }

/* 标题下一条发丝线：从左侧量出来，蓝 → 青 */
.auth-rule {
  display: block;
  width: 46px;
  height: 2px;
  margin: 2px 0 16px;
  border-radius: 2px;
  background: linear-gradient(90deg, var(--accent), var(--accent-2));
  transform-origin: 0 50%;
}

@media (prefers-reduced-motion: no-preference) {
  @keyframes auth-rule-in {
    from {
      opacity: 0;
      transform: scaleX(0);
    }
    to {
      opacity: 1;
      transform: scaleX(1);
    }
  }

  .auth-rule {
    animation: auth-rule-in 640ms var(--ease-expo) 150ms both;
  }

  /* 聚焦：在全局 1px 主色 + ring 之上再加一层冷光，输入框轻抬 1px */
  .auth-form :deep(.el-input__wrapper) {
    transition: box-shadow var(--dur-3) var(--ease-out), transform var(--dur-3) var(--ease-out);
  }

  .auth-form :deep(.el-input__wrapper.is-focus) {
    transform: translateY(-1px);
    box-shadow: 0 0 0 1px var(--accent) inset, 0 0 0 4px var(--accent-soft),
      0 14px 26px -22px var(--accent);
  }

  /* .fx-press 只留 transform 过渡，这里把主按钮原有的悬停过渡补全 */
  .submit-button {
    transition: background-color var(--dur-2) var(--ease-out),
      border-color var(--dur-2) var(--ease-out), color var(--dur-2) var(--ease-out),
      box-shadow var(--dur-3) var(--ease-out), transform var(--dur-1) var(--ease-out),
      scale var(--dur-1) var(--ease-out);
  }
}

/* 全局 .el-button:active 的权重（0,3,0）压过 .fx-press:active（0,2,0），
   按压改用独立的 scale 属性：与 transform 合算，不和它抢 */
.submit-button:active {
  scale: 0.978;
}

/* 验证码取景框：悬停描边亮起，按下回缩（transform 过渡要自己带上） */
.captcha-img {
  transition: border-color var(--dur-2) var(--ease-out), box-shadow var(--dur-2) var(--ease-out),
    transform var(--dur-2) var(--ease-out);
}

@media (hover: hover) and (pointer: fine) {
  .captcha-img:hover {
    border-color: var(--accent-line);
    box-shadow: 0 6px 16px -14px var(--accent);
  }
}
</style>
