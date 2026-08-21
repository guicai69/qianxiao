<template>
  <router-view v-slot="{ Component }">
    <transition name="fade-slide" mode="out-in">
      <component :is="Component" />
    </transition>
  </router-view>
</template>

<script setup>
import { onMounted } from 'vue'
import api from '@/api'
import { useUserStore } from '@/store'

const userStore = useUserStore()

// 应用启动时校验会话：token 存在则拉取最新用户信息；
// 若已过期，拦截器会尝试刷新 token，刷新失败则自动登出。
onMounted(async () => {
  if (!userStore.token) return
  try {
    const res = await api.get('users/me/')
    if (res?.data) userStore.setUserInfo(res.data)
  } catch {
    // 401 已由拦截器统一处理（刷新 token 或自动登出）
  }
})
</script>

<style>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.4s ease;
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}
</style>
