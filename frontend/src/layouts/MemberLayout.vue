<template>
  <div class="member-layout">
    <header class="member-header">
      <div class="brand" @click="goHome">
        <span class="brand-icon"><el-icon :size="22"><Medal /></el-icon></span>
        <strong>羽毛球馆预约</strong>
      </div>

      <nav class="member-nav" v-if="userStore.isLoggedIn">
        <RouterLink to="/" class="nav-link" exact-active-class="active">首页</RouterLink>
        <RouterLink to="/venues" class="nav-link" active-class="active">选择场馆</RouterLink>
        <RouterLink to="/orders" class="nav-link" active-class="active">我的订单</RouterLink>
        <RouterLink to="/payments" class="nav-link" active-class="active">支付记录</RouterLink>
        <RouterLink to="/profile" class="nav-link" active-class="active">个人中心</RouterLink>
      </nav>

      <div class="member-actions">
        <el-button
          v-if="userStore.isAdmin || userStore.isReception"
          type="primary"
          plain
          round
          size="small"
          @click="goHome"
        >
          <el-icon class="el-icon--left"><Back /></el-icon>返回管理后台
        </el-button>
        <template v-if="userStore.isLoggedIn">
          <div class="balance-chip">
            <el-icon><Wallet /></el-icon>
            <span>¥{{ userStore.userInfo?.balance || 0 }}</span>
          </div>
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-entry">
              <span class="avatar">{{ initial }}</span>
              <span class="user-name">{{ userStore.userInfo?.nickname || userStore.userInfo?.phone }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <el-button type="primary" round @click="$router.push('/login')">登录</el-button>
          <el-button round @click="$router.push('/register')">注册</el-button>
        </template>
      </div>
    </header>

    <main class="member-main">
      <router-view />
    </main>

    <footer class="member-footer">羽毛球馆预约管理系统</footer>
  </div>
</template>

<script setup>
import { computed } from "vue"
import { useRouter } from "vue-router"
import { useUserStore } from "@/store"
import { Medal, Wallet, ArrowDown, Back } from "@element-plus/icons-vue"

const userStore = useUserStore()
const router = useRouter()

const initial = computed(() =>
  (userStore.userInfo?.nickname || userStore.userInfo?.phone || "U").slice(0, 1)
)

function goHome() {
  if (userStore.isAdmin) router.push("/admin/dashboard")
  else if (userStore.isReception) router.push("/reception/dashboard")
  else router.push("/")
}

function handleCommand(cmd) {
  if (cmd === "logout") {
    userStore.clearToken()
    router.push("/")
  }
  if (cmd === "profile") router.push("/profile")
}
</script>

<style scoped>
.member-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--mui-bg);
}

.member-header {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  min-height: 68px;
  padding: 0 28px;
  background: var(--mui-surface);
  border-bottom: 1px solid var(--mui-border);
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  white-space: nowrap;
}

.brand-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border-radius: 12px;
  color: var(--mui-primary);
  background: var(--mui-primary-soft);
}

.brand strong {
  color: var(--mui-text);
  font-size: 17px;
  font-weight: 800;
}

.member-nav {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0 auto;
}

.nav-link {
  padding: 8px 14px;
  border-radius: 10px;
  color: #475569;
  font-size: 14px;
  font-weight: 600;
  transition: background-color 0.16s ease, color 0.16s ease;
}

.nav-link:hover {
  color: var(--mui-primary);
  background: #f1f5f9;
}

.nav-link.active {
  color: var(--mui-primary-hover);
  background: var(--mui-primary-soft);
  font-weight: 700;
}

.member-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.balance-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  height: 34px;
  padding: 0 12px;
  border: 1px solid #dbeafe;
  border-radius: 999px;
  color: var(--mui-primary-hover);
  background: #eff6ff;
  font-weight: 700;
}

.user-entry {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  color: #ffffff;
  background: var(--mui-primary);
  font-weight: 800;
}

.user-name {
  color: var(--mui-text);
  font-weight: 700;
  max-width: 110px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.member-main {
  flex: 1;
  width: 100%;
  padding: 28px 24px 56px;
}

.member-footer {
  padding: 18px;
  text-align: center;
  color: var(--mui-muted);
  font-size: 12px;
  border-top: 1px solid var(--mui-border);
  background: var(--mui-surface);
}

@media (max-width: 1024px) {
  .member-header {
    flex-wrap: wrap;
    padding: 12px 16px;
    gap: 10px;
  }

  .member-nav {
    order: 3;
    width: 100%;
    overflow-x: auto;
    justify-content: flex-start;
    padding-bottom: 2px;
  }
}

@media (max-width: 640px) {
  .member-actions .user-name,
  .balance-chip {
    display: none;
  }

  .member-main {
    padding: 18px 14px 40px;
  }
}
</style>
