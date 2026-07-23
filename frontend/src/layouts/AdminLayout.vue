<template>
  <el-container class="admin-layout">
    <el-aside width="220px">
      <div class="logo">🏸 羽毛球馆管理</div>
      <el-menu router :default-active="$route.path" background-color="#304156" text-color="#bfcbd9" active-text-color="#409EFF">
        <!-- Menu items will be added per role -->
      </el-menu>
    </el-aside>
    <el-container>
      <el-header>
        <span>{{ userInfo?.username || '管理员' }}</span>
        <el-button type="danger" link @click="logout">退出登录</el-button>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useUserStore } from '@/store'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()
const userInfo = userStore.userInfo

function logout() {
  userStore.clearToken()
  router.push('/login')
}
</script>

<style scoped>
.admin-layout { height: 100vh; }
.el-aside { background-color: #304156; overflow-x: hidden; }
.logo { color: #fff; text-align: center; padding: 16px 0; font-size: 16px; font-weight: bold; }
.el-header { background: #fff; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #e6e6e6; }
.el-main { background: #f0f2f5; }
</style>
