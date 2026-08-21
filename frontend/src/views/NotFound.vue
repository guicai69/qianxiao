<template>
  <div class="not-found">
    <div class="nf-inner">
      <span class="nf-icon"><el-icon :size="40"><Medal /></el-icon></span>
      <h1>404</h1>
      <p class="nf-title">页面不存在</p>
      <p class="nf-desc">您访问的页面可能已被移除或地址有误。</p>
      <div class="nf-actions">
        <el-button type="primary" size="large" round @click="goHome">
          <el-icon class="el-icon--left"><HomeFilled /></el-icon>返回首页
        </el-button>
        <el-button size="large" round @click="$router.back()">
          <el-icon class="el-icon--left"><Back /></el-icon>返回上页
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router"
import { useUserStore } from "@/store"
import { Medal, HomeFilled, Back } from "@element-plus/icons-vue"

const router = useRouter()
const userStore = useUserStore()

function goHome() {
  if (userStore.isAdmin) router.push("/admin/dashboard")
  else if (userStore.isReception) router.push("/reception/dashboard")
  else router.push("/")
}
</script>

<style scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: var(--mui-bg);
}

.nf-inner {
  text-align: center;
  max-width: 460px;
}

.nf-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  border-radius: 24px;
  color: var(--mui-primary);
  background: var(--mui-primary-soft);
}

.nf-inner h1 {
  margin: 24px 0 0;
  font-size: 88px;
  font-weight: 800;
  line-height: 1;
  color: var(--mui-primary);
  letter-spacing: 2px;
}

.nf-title {
  margin: 16px 0 8px;
  font-size: 20px;
  font-weight: 800;
  color: var(--mui-text);
}

.nf-desc {
  margin: 0 0 28px;
  color: var(--mui-muted);
  font-size: 14px;
}

.nf-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
