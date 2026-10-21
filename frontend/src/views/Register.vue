<template>
  <AuthShell>
    <!-- 门面换幕：与登录页同一套深蓝面 + 三团极光，两页换幕一致 -->
    <div class="auth-aurora" data-plane="deep" aria-hidden="true">
      <span class="fx-aurora__blob"></span>
      <span class="fx-aurora__blob fx-aurora__blob--b"></span>
      <span class="fx-aurora__blob fx-aurora__blob--c"></span>
    </div>

    <h1 class="auth-title fx-rise fx-ink-gradient">创建会员账号</h1>
    <span class="auth-rule" aria-hidden="true"></span>
    <p class="auth-sub fx-rise">注册后即可预约场地。累计消费满 ¥500 升银卡，满 ¥2000 升金卡。</p>

    <el-form ref="formRef" :model="form" :rules="rules" size="large" class="auth-form fx-rise" @submit.prevent>
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
        />
      </el-form-item>
      <el-form-item prop="captchaCode">
        <div class="captcha-row">
          <el-input
            v-model="form.captchaCode"
            placeholder="验证码"
            maxlength="4"
            @keyup.enter="handleRegister"
          />
          <button type="button" class="captcha-img fx-press" aria-label="点击刷新验证码" @click="fetchCaptcha">
            <span v-if="captchaSvg" v-html="captchaSvg"></span>
            <span v-else class="captcha-loading mono">点击获取</span>
          </button>
        </div>
      </el-form-item>

      <el-button type="primary" class="submit-button fx-border-glow fx-press" :loading="loading" @click="handleRegister">
        注册
        <el-icon class="el-icon--right"><ArrowRight /></el-icon>
      </el-button>
    </el-form>

    <div class="auth-switch fx-rise">
      <span>已有账号？</span>
      <el-button link type="primary" @click="$router.push('/login')">立即登录</el-button>
    </div>
  </AuthShell>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Iphone, User, Lock, ArrowRight } from '@element-plus/icons-vue'
import api from '@/api'
import AuthShell from '@/components/brand/AuthShell.vue'

const router = useRouter()
const loading = ref(false)
const formRef = ref(null)
const captchaSvg = ref('')

const form = reactive({ phone: '', nickname: '', password: '', password2: '', captchaId: '', captchaCode: '' })

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
  captchaCode: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
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
        captcha_id: form.captchaId,
        captcha_code: form.captchaCode,
      })
      ElMessage.success('注册成功，请登录')
      router.push('/login')
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
   动效（2026-10）：与 Login 同一套换幕语言，节拍少一格（无演示账号块）
   ========================================================================== */

/* 左半深色面的三团极光：右边界对齐 AuthShell 的 520px 表单栏 */
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

/* 标题渐变墨：让渐变贴着文字走 */
.auth-title {
  width: fit-content;
}

/* 首屏入场节拍：70ms 一步 */
.auth-title { --i: 0; }
.auth-sub { --i: 1; }
.auth-form { --i: 2; }
.auth-switch { --i: 3; }

/* 标题下一条发丝线：蓝 → 青 */
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

/* 全局 .el-button:active 的权重压过 .fx-press:active，按压改用独立的 scale 属性 */
.submit-button:active {
  scale: 0.978;
}

/* 验证码取景框：悬停描边亮起，按下回缩 */
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
