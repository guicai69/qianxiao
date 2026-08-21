<template>
  <div class="home">
    <h1>欢迎来到羽毛球馆预约系统</h1>
    <p>选择场馆，预约您心仪的场地和时段</p>
    <el-button type="primary" size="large" @click="handleStartBooking">开始预约</el-button>
  </div>
</template>

<style scoped>
.home { text-align: center; padding: 60px 20px; }
.home h1 { color: #303133; }
.home p { color: #909399; margin: 16px 0 24px; }
</style>

<script setup>
import { useUserStore } from '@/store'
import { useRouter } from 'vue-router'
const userStore = useUserStore()
const router = useRouter()

function handleStartBooking() {
  if (!userStore.isLoggedIn) {
    router.push('/login')
  } else if (userStore.isAdmin) {
    router.push('/admin/dashboard')
  } else if (userStore.isReception) {
    router.push('/admin/dashboard')
  } else {
    router.push('/venues')
  }
}
</script>


