<template>
  <div class="member-layout">
    <header class="member-header">
      <div class="logo" @click="$router.push('/')">🏸 羽毛球馆预约</div>
      <nav>
        <router-link to="/">首页</router-link>
        <template v-if="userStore.isLoggedIn">
          <router-link to="/profile">个人中心</router-link>
          <el-tag :type="levelTag" size="small">余额 ¥{{ userStore.userInfo?.balance || 0 }}</el-tag>
          <span>{{ userStore.userInfo?.nickname || userStore.userInfo?.phone }}</span>
          <el-button type="danger" size="small" link @click="handleLogout">退出</el-button>
        </template>
        <template v-else>
          <el-button type="primary" size="small" @click="$router.push('/login')">登录</el-button>
          <el-button size="small" @click="$router.push('/register')">注册</el-button>
        </template>
      </nav>
    </header>
    <main>
      <router-view />
    </main>
    <footer>© 2025 Badminton Venue Management</footer>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useUserStore } from '@/store'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()

const levelTag = computed(() =>
  userStore.userInfo?.level === 'gold' ? 'warning' : 'info'
)

function handleLogout() {
  userStore.clearToken()
  router.push('/')
}
</script>

<style scoped>
.member-layout { min-height: 100vh; display: flex; flex-direction: column; }
.member-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 24px; height: 60px; background: #fff;
  box-shadow: 0 1px 4px rgba(0,0,0,.08);
}
.member-header nav { display: flex; align-items: center; gap: 20px; }
.member-header nav a { text-decoration: none; color: #333; }
.logo { font-size: 18px; font-weight: bold; color: #409EFF; cursor: pointer; }
main { flex: 1; padding: 20px; }
footer { text-align: center; padding: 16px; color: #999; font-size: 12px; }
</style>
