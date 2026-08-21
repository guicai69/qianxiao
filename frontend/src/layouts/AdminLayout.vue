<template>
  <el-container class="admin-shell">
    <el-aside :width="collapsed ? '76px' : '248px'" class="mui-sidebar">
      <div class="brand" :class="{ collapsed }" @click="goHome">
        <span class="brand-icon"><el-icon :size="24"><Medal /></el-icon></span>
        <div v-if="!collapsed" class="brand-copy">
          <strong>羽毛球馆管理</strong>
          <span>Venue Console</span>
        </div>
      </div>

      <div class="menu-scroll">
        <div v-if="!collapsed" class="menu-caption">{{ menuCaption }}</div>
        <el-menu
          router
          :default-active="activeMenu"
          :collapse="collapsed"
          :collapse-transition="false"
          class="mui-menu"
        >
          <el-menu-item v-if="userStore.isAdmin" index="/admin/dashboard">
            <el-icon><DataAnalysis /></el-icon>
            <template #title>数据看板</template>
          </el-menu-item>
          <el-menu-item v-if="userStore.isReception" index="/reception/dashboard">
            <el-icon><Monitor /></el-icon>
            <template #title>操作台</template>
          </el-menu-item>
          <el-menu-item v-if="userStore.isAdmin" index="/admin/users">
            <el-icon><User /></el-icon>
            <template #title>用户管理</template>
          </el-menu-item>
          <el-menu-item index="/admin/venues">
            <el-icon><OfficeBuilding /></el-icon>
            <template #title>场馆管理</template>
          </el-menu-item>
          <el-menu-item index="/admin/bookings">
            <el-icon><Tickets /></el-icon>
            <template #title>预约管理</template>
          </el-menu-item>
          <el-menu-item index="/admin/payments">
            <el-icon><Wallet /></el-icon>
            <template #title>支付记录</template>
          </el-menu-item>
          <el-menu-item index="/admin/announcements">
            <el-icon><Bell /></el-icon>
            <template #title>公告管理</template>
          </el-menu-item>
        </el-menu>
      </div>
    </el-aside>

    <el-container class="right-container">
      <el-header class="mui-topbar">
        <div class="topbar-left">
          <el-button class="collapse-btn" text @click="toggleCollapse">
            <el-icon :size="20"><Fold v-if="!collapsed" /><Expand v-else /></el-icon>
          </el-button>
          <div class="topbar-title">
            <h2>{{ pageTitle }}</h2>
            <span>{{ breadcrumb }}</span>
          </div>
        </div>

        <div class="topbar-right">
          <el-tag :type="roleTag" effect="light" round>{{ roleLabel }}</el-tag>
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-entry">
              <span class="avatar">{{ initial }}</span>
              <div class="user-copy">
                <strong>{{ userStore.userInfo?.nickname || userStore.userInfo?.phone }}</strong>
                <span>{{ userStore.userInfo?.phone }}</span>
              </div>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>个人中心
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="mui-main">
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from "vue"
import { useRoute, useRouter } from "vue-router"
import { useUserStore } from "@/store"
import {
  DataAnalysis,
  User,
  Monitor,
  OfficeBuilding,
  Tickets,
  Wallet,
  Bell,
  Medal,
  Fold,
  Expand,
  ArrowDown,
  SwitchButton,
} from "@element-plus/icons-vue"

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()
const collapsed = ref(false)

const roleTag = computed(() =>
  ({ admin: "danger", reception: "warning", member: "success" }[userStore.role])
)
const roleLabel = computed(() =>
  ({ admin: "管理员", reception: "前台", member: "会员" }[userStore.role])
)
const pageTitle = computed(() => route.meta.title || "管理后台")
const breadcrumb = computed(() => `${roleLabel.value} / ${pageTitle.value}`)
const menuCaption = computed(() => (userStore.isReception ? "前台工作台" : "管理中心"))
const initial = computed(() =>
  (userStore.userInfo?.nickname || userStore.userInfo?.phone || "U").slice(0, 1)
)

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith("/admin/venues")) return "/admin/venues"
  if (path.startsWith("/admin")) return path
  if (path.startsWith("/reception")) return path
  return "/"
})

function toggleCollapse() {
  collapsed.value = !collapsed.value
}

function goHome() {
  if (userStore.isReception) router.push("/reception/dashboard")
  else router.push("/admin/dashboard")
}

function handleCommand(cmd) {
  if (cmd === "logout") {
    userStore.clearToken()
    router.push("/login")
  }
  if (cmd === "profile") router.push("/profile")
}
</script>

<style scoped>
.admin-shell {
  height: 100vh;
  width: 100%;
  background: var(--mui-bg);
}

.mui-sidebar {
  display: flex;
  flex-direction: column;
  background: var(--mui-surface);
  border-right: 1px solid var(--mui-border);
  transition: width 0.24s ease;
  overflow: hidden;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 72px;
  padding: 0 18px;
  cursor: pointer;
  border-bottom: 1px solid var(--mui-border-soft);
  white-space: nowrap;
}

.brand.collapsed {
  justify-content: center;
  padding: 0;
}

.brand-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  color: var(--mui-primary);
  background: var(--mui-primary-soft);
  flex: 0 0 40px;
}

.brand-copy {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.brand-copy strong {
  color: var(--mui-text);
  font-size: 16px;
  line-height: 22px;
}

.brand-copy span {
  color: var(--mui-muted);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.menu-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0 20px;
}

.menu-caption {
  padding: 12px 24px 8px;
  color: #94a3b8;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.mui-menu {
  background: transparent;
  padding: 0 6px;
}

.right-container {
  background: var(--mui-bg);
}

.mui-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  height: 72px;
  padding: 0 24px;
  background: var(--mui-surface);
  border-bottom: 1px solid var(--mui-border);
}

.topbar-left,
.topbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.collapse-btn {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  color: var(--mui-muted);
}

.collapse-btn:hover {
  color: var(--mui-primary);
  background: var(--mui-primary-soft);
}

.topbar-title {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.topbar-title h2 {
  margin: 0;
  color: var(--mui-text);
  font-size: 18px;
  font-weight: 800;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.topbar-title span {
  margin-top: 2px;
  color: var(--mui-muted);
  font-size: 12px;
}

.user-entry {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 10px;
  border: 1px solid var(--mui-border);
  border-radius: 12px;
  background: var(--mui-surface);
  cursor: pointer;
  transition: border-color 0.16s ease, box-shadow 0.16s ease;
}

.user-entry:hover {
  border-color: #bfdbfe;
  box-shadow: var(--mui-shadow);
}

.avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 10px;
  color: #ffffff;
  background: var(--mui-primary);
  font-weight: 800;
}

.user-copy {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.user-copy strong {
  color: var(--mui-text);
  font-size: 13px;
  line-height: 18px;
  max-width: 140px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-copy span {
  color: var(--mui-muted);
  font-size: 11px;
}

.mui-main {
  padding: 24px;
  background: var(--mui-bg);
  overflow-y: auto;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.28s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

@media (max-width: 900px) {
  .mui-sidebar {
    position: fixed;
    z-index: 20;
    height: 100vh;
    box-shadow: var(--mui-shadow-lg);
  }

  .right-container {
    margin-left: 76px;
    width: calc(100% - 76px);
  }

  .user-copy {
    display: none;
  }
}
</style>
