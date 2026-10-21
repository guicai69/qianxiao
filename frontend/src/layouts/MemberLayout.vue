<template>
  <div class="member-layout">
    <!-- 滚动进度：原生 scroll() 时间线驱动，零 JS；不支持就静默不显示 -->
    <div class="fx-progress" aria-hidden="true"></div>

    <!-- 球馆栏：会员端从头到尾一条深色顶栏，跟后台的深色侧栏是同一套语言 -->
    <header class="member-header" >
      <div class="header-inner">
        <button class="brand" type="button" @click="goHome">
          <span class="brand-mark">
            <svg viewBox="0 0 24 24" width="19" height="19" aria-hidden="true">
              <rect x="4.2" y="3" width="15.6" height="18" rx="1.4" fill="none" stroke="currentColor" stroke-width="1.5" />
              <path d="M4.2 12h15.6" stroke="currentColor" stroke-width="1.5" />
              <path d="M12 3v18" stroke="currentColor" stroke-width="1" opacity=".45" />
            </svg>
          </span>
          <span class="brand-copy">
            <strong>羽毛球馆预约</strong>
            <span class="mono">BADMINTON COURT</span>
          </span>
        </button>

        <nav v-if="userStore.isLoggedIn" class="member-nav">
          <RouterLink to="/" class="nav-link" exact-active-class="active">首页</RouterLink>
          <RouterLink to="/venues" class="nav-link" active-class="active">选场馆</RouterLink>
          <RouterLink to="/orders" class="nav-link" active-class="active">我的订单</RouterLink>
          <RouterLink to="/payments" class="nav-link" active-class="active">支付记录</RouterLink>
          <RouterLink to="/activities" class="nav-link" active-class="active">活动课程</RouterLink>
          <RouterLink to="/coupons" class="nav-link" active-class="active">优惠券</RouterLink>
          <RouterLink to="/profile" class="nav-link" active-class="active">个人中心</RouterLink>
        </nav>

        <div class="member-actions">
          <el-button
            v-if="userStore.isAdmin || userStore.isReception"
            plain
            round
            size="small"
            class="back-console"
            @click="goHome"
          >
            <el-icon class="el-icon--left"><Back /></el-icon>返回管理后台
          </el-button>

          <template v-if="userStore.isLoggedIn">
            <RouterLink to="/profile" class="balance-chip mono">
              <el-icon><Wallet /></el-icon>
              <span>¥{{ balance }}</span>
            </RouterLink>

            <el-dropdown trigger="click" @command="handleCommand">
              <button class="user-entry" type="button">
                <span class="avatar">{{ initial }}</span>
                <span class="user-name">{{ userStore.userInfo?.nickname || userStore.userInfo?.phone }}</span>
                <el-icon class="chev"><ArrowDown /></el-icon>
              </button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                  <el-dropdown-item command="orders">我的订单</el-dropdown-item>
                  <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>

          <template v-else>
            <button class="link-ghost" type="button" @click="$router.push('/login')">登录</button>
            <el-button type="primary" round size="small" @click="$router.push('/register')">注册</el-button>
          </template>
        </div>
      </div>
    </header>

    <main class="member-main">
      <router-view />
    </main>

    <footer class="member-footer" >
      <div class="footer-inner">
        <span class="footer-mark mono">羽毛球馆预约管理系统</span>
        <span class="footer-note">毕业设计 · Django REST Framework + Vue 3</span>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store'
import { Wallet, ArrowDown, Back } from '@element-plus/icons-vue'

const userStore = useUserStore()
const router = useRouter()

const initial = computed(() =>
  (userStore.userInfo?.nickname || userStore.userInfo?.phone || 'U').slice(0, 1)
)

const balance = computed(() => Number(userStore.userInfo?.balance || 0).toFixed(2))

function goHome() {
  if (userStore.isAdmin) router.push('/admin/dashboard')
  else if (userStore.isReception) router.push('/reception/dashboard')
  else router.push('/')
}

function handleCommand(cmd) {
  if (cmd === 'logout') {
    userStore.clearToken()
    router.push('/')
  }
  if (cmd === 'profile') router.push('/profile')
  if (cmd === 'orders') router.push('/orders')
}
</script>

<style scoped>
.member-layout {
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  background: var(--page);
}

/* ---------- 顶栏 ---------- */

.member-header {
  position: sticky;
  top: 0;
  z-index: var(--z-nav);
  height: var(--nav-h);
  background: var(--page);
  border-bottom: 1px solid var(--border);
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  height: 100%;
  max-width: 1320px;
  margin: 0 auto;
  padding: 0 24px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  border: 0;
  background: none;
  padding: 0;
  cursor: pointer;
  white-space: nowrap;
  min-width: 0;
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  flex: 0 0 34px;
  border-radius: 10px;
  color: var(--accent);
  border: 1px solid var(--border);
  background: var(--surface);
}

.brand-copy {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  min-width: 0;
}

.brand-copy strong {
  font-size: var(--fs-14);
  font-weight: 800;
  letter-spacing: -0.01em;
  color: var(--ink-1);
  line-height: 1.25;
}

.brand-copy .mono {
  font-size: 9px;
  letter-spacing: 0.16em;
  color: var(--ink-4);
}

.member-nav {
  display: flex;
  align-items: center;
  gap: 2px;
  margin-left: 20px;
}

.nav-link {
  position: relative;
  padding: 8px 12px;
  border-radius: 9px;
  color: var(--ink-2);
  font-size: var(--fs-13);
  font-weight: 600;
  white-space: nowrap;
  transition: color var(--dur-2) var(--ease-out), background-color var(--dur-2) var(--ease-out);
}

.nav-link:hover {
  color: var(--ink-1);
  background: var(--surface-2);
}

.nav-link.active {
  color: var(--accent);
  font-weight: 700;
}

.nav-link::after {
  content: "";
  position: absolute;
  left: 12px;
  right: 12px;
  bottom: 2px;
  height: 2px;
  border-radius: 2px;
  background: var(--accent);
  transform: scaleX(0);
  transform-origin: left center;
  transition: transform var(--dur-3) var(--ease-out);
}

.nav-link.active::after {
  transform: scaleX(1);
}

.member-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 0 0 auto;
  margin-left: auto;
}

.balance-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 32px;
  padding: 0 12px;
  border: 1px solid var(--accent-line);
  border-radius: 999px;
  color: var(--accent);
  background: var(--accent-soft);
  font-size: var(--fs-13);
  font-weight: 700;
  transition: border-color var(--dur-2) var(--ease-out);
}

.balance-chip:hover {
  border-color: var(--accent);
}

.user-entry {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 32px;
  padding: 0 8px 0 4px;
  border: 1px solid transparent;
  border-radius: 999px;
  background: none;
  cursor: pointer;
  transition: border-color var(--dur-2) var(--ease-out), background-color var(--dur-2) var(--ease-out);
}

.user-entry:hover {
  border-color: var(--border);
  background: var(--surface);
}

.avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  flex: 0 0 26px;
  border-radius: 50%;
  color: var(--on-accent);
  background: var(--accent);
  font-size: var(--fs-12);
  font-weight: 800;
}

.user-name {
  color: var(--ink-2);
  font-size: var(--fs-13);
  font-weight: 600;
  max-width: 96px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chev {
  font-size: 12px;
  color: var(--ink-4);
}

.link-ghost {
  border: 0;
  background: none;
  padding: 6px 4px;
  color: var(--ink-3);
  font-size: var(--fs-13);
  font-weight: 600;
  cursor: pointer;
  transition: color var(--dur-2) var(--ease-out);
}

.link-ghost:hover {
  color: var(--accent);
}

.back-console {
  --el-button-bg-color: transparent;
  --el-button-text-color: var(--accent);
  --el-button-border-color: var(--accent-line);
  --el-button-hover-bg-color: var(--accent-soft);
  --el-button-hover-text-color: var(--accent);
  --el-button-hover-border-color: var(--accent);
}

/* ---------- 内容区 ---------- */

.member-main {
  flex: 1;
  width: 100%;
}

/* ---------- 页脚 ---------- */

.member-footer {
  background: var(--page);
  border-top: 1px solid var(--border);
}

.footer-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  max-width: 1320px;
  margin: 0 auto;
  padding: 22px 24px;
}

.footer-mark {
  font-size: var(--fs-12);
  font-weight: 700;
  letter-spacing: 0.1em;
  color: var(--ink-3);
}

.footer-note {
  font-size: var(--fs-12);
  color: var(--ink-4);
}

/* ---------- 动效升级（2026-10） ---------- */

/* 顶栏随滚动变玻璃：滚过 140px 后底色转半透明、加模糊与一道浅影 */
@media (prefers-reduced-motion: no-preference) {
  @supports (animation-timeline: scroll()) {
    .member-header {
      animation: header-glass linear both;
      animation-timeline: scroll(root block);
      animation-range: 0 140px;
    }
  }
}

@keyframes header-glass {
  from {
    background-color: rgba(238, 242, 248, 1);
    -webkit-backdrop-filter: blur(0px);
    backdrop-filter: blur(0px);
    box-shadow: none;
  }
  to {
    background-color: rgba(243, 246, 251, 0.78);
    -webkit-backdrop-filter: blur(14px) saturate(1.3);
    backdrop-filter: blur(14px) saturate(1.3);
    box-shadow: 0 10px 30px -26px rgba(16, 36, 72, 0.55);
  }
}

/* 品牌标记：悬停时像被人翻了一下球拍面 */
.brand-mark {
  transition: transform var(--dur-3) var(--ease-spring), border-color var(--dur-2) var(--ease-out),
    background-color var(--dur-2) var(--ease-out);
}

@media (hover: hover) and (pointer: fine) {
  .brand:hover .brand-mark {
    transform: rotate(-4deg) scale(1.05);
    border-color: var(--accent-line);
    background: var(--accent-soft);
  }
}

/* 导航：当前项垫一层很淡的底色，悬停时下划线先长一半 */
.nav-link.active {
  background: var(--accent-soft);
}

@media (hover: hover) and (pointer: fine) {
  .nav-link:hover::after {
    transform: scaleX(0.55);
  }
}

.nav-link.active::after {
  box-shadow: 0 0 10px var(--accent-line);
}

/* 头像：悬停轻轻外扩 */
.avatar {
  transition: box-shadow var(--dur-3) var(--ease-out), transform var(--dur-2) var(--ease-out);
}

@media (hover: hover) and (pointer: fine) {
  .user-entry:hover .avatar {
    transform: translateY(-1px);
    box-shadow: 0 0 0 3px var(--accent-soft);
  }
}

/* 页脚：一条极细的渐变分隔线代替灰线 */
.member-footer {
  position: relative;
}

.member-footer::before {
  content: "";
  position: absolute;
  inset: 0 0 auto 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent-line) 22%, var(--border) 60%, transparent);
}

/* ---------- 断点 ---------- */

@media (max-width: 1080px) {
  .header-inner {
    flex-wrap: wrap;
    height: auto;
    padding: 10px 16px;
    gap: 8px;
  }

  .member-header {
    height: auto;
  }

  .member-nav {
    order: 3;
    width: 100%;
    margin: 0;
    overflow-x: auto;
    scrollbar-width: none;
    padding-bottom: 2px;
  }

  .member-nav::-webkit-scrollbar {
    display: none;
  }
}

@media (max-width: 640px) {
  .user-name,
  .brand-copy .mono {
    display: none;
  }

  .brand-copy strong {
    font-size: var(--fs-13);
  }

  .footer-inner {
    padding: 18px 16px;
  }
}
</style>
