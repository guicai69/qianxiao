<template>
  <!-- 路由出口。
       这里刻意【不用】 <transition mode="out-in"> 包 <component :is>：
       实测在"登录成功 → 应用内跳转"这条路径上，out-in 会卡在占位注释上
       （旧节点已移除、新节点不再插入，整页白屏且不报任何错），
       给 :duration 也没用。改成 key 换页 + CSS 入场动画，效果一样但不依赖
       那套占位/事件逻辑。 -->
  <router-view v-slot="{ Component, route }">
    <component :is="Component" :key="route.path" class="route-view" />
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
/* 换页入场：只动 opacity / transform。
   作者状态是"已就位"，动画从"没就位"进来 —— 所以减少动态效果兜底
   把时长压到 0.01ms 时，页面直接停在正常状态，不会白屏。 */
@media (prefers-reduced-motion: no-preference) {
  .route-view {
    animation: route-in 260ms var(--ease-out) both;
  }
}

@keyframes route-in {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: none;
  }
}
</style>
