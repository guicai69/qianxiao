<template>
  <div class="member-layout">
    <header class="member-header">
      <div class="logo">🏸 羽毛球馆预约</div>
      <nav>
        <router-link to="/">首页</router-link>
        <router-link to="/my-bookings">我的预约</router-link>
        <router-link to="/profile">个人中心</router-link>
        <el-button v-if="!userStore.token" type="primary" size="small" @click="$router.push('/login')">登录</el-button>
        <el-button v-else type="danger" size="small" link @click="logout">退出</el-button>
      </nav>
    </header>
    <main>
      <router-view />
    </main>
    <footer>© 2025 Badminton Venue Management</footer>
  </div>
</template>

<script setup>
import { useUserStore } from '@/store'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()

function logout() {
  userStore.clearToken()
  router.push('/login')
}
</script>

<style scoped>
.member-layout { min-height: 100vh; display: flex; flex-direction: column; }
.member-header { display: flex; align-items: center; justify-content: space-between; padding: 0 24px; height: 60px; background: #fff; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
.member-header nav { display: flex; align-items: center; gap: 20px; }
.member-header nav a { text-decoration: none; color: #333; }
.logo { font-size: 18px; font-weight: bold; color: #409EFF; }
main { flex: 1; padding: 20px; }
footer { text-align: center; padding: 16px; color: #999; font-size: 12px; }
</style>
