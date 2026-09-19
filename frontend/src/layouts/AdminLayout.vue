<template>
  <el-container class="admin-shell">
    <el-aside :width="railCollapsed ? '76px' : '248px'" class="rail">
      <div class="brand" :class="{ collapsed: railCollapsed }" @click="goHome">
        <span class="brand-mark">
          <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
            <rect
              x="4.2"
              y="3"
              width="15.6"
              height="18"
              rx="1.4"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
            />
            <path d="M4.2 12h15.6" stroke="currentColor" stroke-width="1.5" />
            <path d="M12 3v18" stroke="currentColor" stroke-width="1" opacity=".45" />
          </svg>
        </span>
        <span v-if="!railCollapsed" class="brand-copy">
          <strong>羽毛球馆管理</strong>
          <span class="mono">VENUE CONSOLE</span>
        </span>
      </div>

      <div class="menu-scroll">
        <div v-if="!railCollapsed" class="menu-caption">{{ menuCaption }}</div>
        <el-menu
          router
          :default-active="activeMenu"
          :collapse="railCollapsed"
          :collapse-transition="false"
          class="rail-menu"
        >
          <el-menu-item v-for="item in navItems" :key="item.index" :index="item.index">
            <el-icon><component :is="item.icon" /></el-icon>
            <template #title>{{ item.label }}</template>
          </el-menu-item>
        </el-menu>
      </div>
    </el-aside>

    <el-container class="right-container">
      <el-header class="topbar">
        <div class="topbar-left">
          <el-button class="icon-btn collapse-btn" text aria-label="折叠导航" @click="toggleCollapse">
            <el-icon :size="20"><Fold v-if="!railCollapsed" /><Expand v-else /></el-icon>
          </el-button>
          <el-button class="icon-btn hamburger" text aria-label="打开导航" @click="drawerOpen = true">
            <el-icon :size="20"><Menu /></el-icon>
          </el-button>
          <div class="topbar-title">
            <h2>{{ pageTitle }}</h2>
            <span class="mono">{{ breadcrumb }}</span>
          </div>
        </div>

        <div class="topbar-right">
          <el-tag :type="roleTag" effect="light" round>{{ roleLabel }}</el-tag>
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-entry">
              <span class="avatar">{{ initial }}</span>
              <div class="user-copy">
                <strong>{{ userStore.userInfo?.nickname || userStore.userInfo?.phone }}</strong>
                <span class="mono">{{ userStore.userInfo?.phone }}</span>
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

      <el-main class="main">
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>

    <!-- 窄屏抽屉：同一份菜单，窄屏下侧栏整体隐藏 -->
    <el-drawer
      v-model="drawerOpen"
      direction="ltr"
      size="248px"
      :with-header="false"
      class="rail-drawer"
    >
      <div class="rail rail--drawer">
        <div class="brand" @click="goHome">
          <span class="brand-mark">
            <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
              <rect
                x="4.2"
                y="3"
                width="15.6"
                height="18"
                rx="1.4"
                fill="none"
                stroke="currentColor"
                stroke-width="1.5"
              />
              <path d="M4.2 12h15.6" stroke="currentColor" stroke-width="1.5" />
              <path d="M12 3v18" stroke="currentColor" stroke-width="1" opacity=".45" />
            </svg>
          </span>
          <span class="brand-copy">
            <strong>羽毛球馆管理</strong>
            <span class="mono">VENUE CONSOLE</span>
          </span>
        </div>
        <div class="menu-scroll">
          <div class="menu-caption">{{ menuCaption }}</div>
          <el-menu router :default-active="activeMenu" class="rail-menu">
            <el-menu-item v-for="item in navItems" :key="item.index" :index="item.index">
              <el-icon><component :is="item.icon" /></el-icon>
              <template #title>{{ item.label }}</template>
            </el-menu-item>
          </el-menu>
        </div>
      </div>
    </el-drawer>
  </el-container>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from "vue"
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
  Fold,
  Expand,
  Menu,
  ArrowDown,
  SwitchButton,
} from "@element-plus/icons-vue"

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()

const collapsed = ref(false)
const drawerOpen = ref(false)
const autoCollapse = ref(false)

/* 折叠状态：手动折叠 + 窄屏自动折叠取或，原手动逻辑保持原样 */
const railCollapsed = computed(() => collapsed.value || autoCollapse.value)

/* 导航顺序、权限判断、路由 index 与原来逐条一致 */
const navItems = computed(() => {
  const items = []
  if (userStore.isAdmin)
    items.push({ index: "/admin/dashboard", label: "数据看板", icon: DataAnalysis })
  // 管理员也放进来：一个账号就能演示"看数据 + 到店核销"整条链路
  if (userStore.isAdmin || userStore.isReception)
    items.push({ index: "/reception/dashboard", label: "操作台", icon: Monitor })
  if (userStore.isAdmin) items.push({ index: "/admin/users", label: "用户管理", icon: User })
  items.push({ index: "/admin/venues", label: "场馆管理", icon: OfficeBuilding })
  items.push({ index: "/admin/bookings", label: "预约管理", icon: Tickets })
  items.push({ index: "/admin/payments", label: "支付记录", icon: Wallet })
  items.push({ index: "/admin/announcements", label: "公告管理", icon: Bell })
  return items
})

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

watch(
  () => route.path,
  () => {
    drawerOpen.value = false
  }
)

/* 窄屏判定放在 JS 里，侧栏宽度与 el-menu 的折叠态才能同步 */
const railQuery = typeof window !== "undefined" ? matchMedia("(max-width: 1100px)") : null
const phoneQuery = typeof window !== "undefined" ? matchMedia("(max-width: 820px)") : null

function onRailChange(e) {
  autoCollapse.value = e.matches
}

function onPhoneChange(e) {
  if (!e.matches) drawerOpen.value = false
}

onMounted(() => {
  autoCollapse.value = !!railQuery?.matches
  railQuery?.addEventListener("change", onRailChange)
  phoneQuery?.addEventListener("change", onPhoneChange)
})

onUnmounted(() => {
  railQuery?.removeEventListener("change", onRailChange)
  phoneQuery?.removeEventListener("change", onPhoneChange)
})
</script>

<style scoped>
.admin-shell {
  height: 100vh;
  width: 100%;
  background: var(--page);
}

/* ---------- 深色侧栏：整页唯一的深色面 ---------- */

.rail {
  display: flex;
  flex-direction: column;
  background: var(--rail);
  border-right: 1px solid var(--rail-border);
  transition: width 0.24s var(--ease-out);
  overflow: hidden;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 72px;
  padding: 0 18px;
  cursor: pointer;
  border-bottom: 1px solid var(--rail-border);
  white-space: nowrap;
  min-width: 0;
}

.brand.collapsed {
  justify-content: center;
  padding: 0;
}

.rail--drawer {
  position: absolute;
  inset: 0;
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  flex: 0 0 34px;
  border-radius: 10px;
  color: var(--rail-accent);
  background: var(--rail-2);
  border: 1px solid var(--rail-border);
}

.brand-copy {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.brand-copy strong {
  color: var(--rail-ink-active);
  font-size: var(--fs-14);
  font-weight: 800;
  letter-spacing: -0.01em;
  line-height: 1.3;
}

.brand-copy .mono {
  font-size: 9px;
  font-weight: 600;
  letter-spacing: 0.16em;
  color: var(--rail-ink);
}

.menu-scroll {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 10px 0 20px;
}

.menu-caption {
  padding: 12px 18px 8px;
  color: var(--rail-ink);
  font-size: var(--fs-11);
  font-weight: 700;
  letter-spacing: var(--track-caps);
}

.rail-menu {
  width: 100%;
  background: transparent;
  border-right: 0;
  padding: 0;
}

.rail-menu :deep(.el-menu-item) {
  margin: 3px 12px;
  height: 44px;
  line-height: 44px;
  border-radius: 10px;
  color: var(--rail-ink);
  font-weight: 600;
}

.rail-menu :deep(.el-menu-item:hover) {
  background: var(--rail-2);
  color: var(--rail-ink-active);
}

.rail-menu :deep(.el-menu-item.is-active) {
  background: rgba(232, 163, 61, 0.13);
  color: var(--rail-accent);
  font-weight: 700;
}

.rail-menu :deep(.el-menu-item.is-active::before) {
  background: var(--rail-accent);
}

.rail-menu.el-menu--collapse :deep(.el-menu-item) {
  margin: 3px 12px;
  padding: 0;
  justify-content: center;
}

/* ---------- 内容区：暖纸面 ---------- */

.right-container {
  background: var(--page);
  min-width: 0;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  height: 72px;
  padding: 0 24px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
}

.topbar-left,
.topbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.icon-btn {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  color: var(--ink-3);
}

.icon-btn:hover {
  color: var(--accent);
  background: var(--accent-soft);
}

.hamburger {
  display: none;
}

.topbar-title {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.topbar-title h2 {
  margin: 0;
  color: var(--ink-1);
  font-size: var(--fs-18);
  font-weight: 800;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.topbar-title .mono {
  margin-top: 2px;
  color: var(--ink-4);
  font-size: var(--fs-11);
  letter-spacing: 0.06em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-entry {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 10px 4px 4px;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--surface);
  cursor: pointer;
  transition: border-color var(--dur-2) var(--ease-out), box-shadow var(--dur-2) var(--ease-out);
}

.user-entry:hover {
  border-color: var(--border-strong);
  box-shadow: var(--shadow);
}

.avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  flex: 0 0 30px;
  border-radius: 50%;
  color: var(--on-accent);
  background: var(--accent);
  font-size: var(--fs-12);
  font-weight: 800;
}

.user-copy {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.user-copy strong {
  color: var(--ink-1);
  font-size: var(--fs-13);
  line-height: 17px;
  max-width: 140px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-copy .mono {
  color: var(--ink-4);
  font-size: var(--fs-11);
}

.main {
  padding: 24px;
  background: var(--page);
  overflow-y: auto;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity var(--dur-3) var(--ease-out), transform var(--dur-3) var(--ease-out);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* ---------- 断点：1100 收成图标栏，820 换抽屉 ---------- */

@media (max-width: 820px) {
  .rail:not(.rail--drawer) {
    display: none;
  }

  .right-container {
    margin-left: 0;
    width: 100%;
  }

  .collapse-btn {
    display: none;
  }

  .hamburger {
    display: inline-flex;
  }

  .topbar {
    height: 64px;
    padding: 0 16px;
  }

  .main {
    padding: 16px;
  }

  .user-copy {
    display: none;
  }
}

@media (max-width: 420px) {
  .topbar-title .mono {
    display: none;
  }
}
</style>

<style>
/* 抽屉被 teleport 到 body，作用域样式够不到，只针对这一个抽屉 */
.rail-drawer .el-drawer__body {
  padding: 0;
  overflow: hidden;
  position: relative;
}
</style>
