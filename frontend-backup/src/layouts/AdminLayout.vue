<template>
  <el-container class="admin-layout">
    <el-aside width="220px">
      <div class="logo">🏸 羽毛球馆管理</div>
      <el-menu
        router
        :default-active="$route.path"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/admin/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据看板</span>
        </el-menu-item>
        <el-menu-item index="/admin/users" v-if="userStore.isAdmin">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-sub-menu index="venue" v-if="userStore.isAdmin || userStore.isReception">
          <template #title>
            <el-icon><OfficeBuilding /></el-icon>
            <span>场馆管理</span>
          </template>
          <el-menu-item index="/admin/venues">
            <el-icon><List /></el-icon>
            <span>场馆列表</span>
          </el-menu-item>
        </el-sub-menu>


        <!-- Reception menu -->
        <template v-if="userStore.isReception">
          <el-menu-item index="/reception/dashboard">
            <el-icon><Monitor /></el-icon>
            <span>操作台</span>
          </el-menu-item>
        </template>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header>
        <span>{{ userStore.userInfo?.nickname || userStore.userInfo?.phone || '用户' }}</span>
        <div>
          <el-tag :type="roleTag" size="small" style="margin-right:12px">{{ roleLabel }}</el-tag>
          <el-button type="danger" link @click="handleLogout">退出登录</el-button>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { DataAnalysis, User, Monitor, OfficeBuilding, List } from '@element-plus/icons-vue'
import { useUserStore } from '@/store'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()

const roleTag = computed(() =>
  ({ admin: 'danger', reception: 'warning', member: 'success' }[userStore.role])
)
const roleLabel = computed(() =>
  ({ admin: '管理员', reception: '前台', member: '会员' }[userStore.role])
)

function handleLogout() {
  userStore.clearToken()
  router.push('/login')
}
</script>

<style scoped>
.admin-layout { height: 100vh; }
.el-aside { background-color: #304156; overflow-x: hidden; }
.logo { color: #fff; text-align: center; padding: 16px 0; font-size: 16px; font-weight: bold; }
.el-header {
  background: #fff; display: flex; align-items: center; justify-content: space-between;
  border-bottom: 1px solid #e6e6e6;
}
.el-main { background: #f0f2f5; }
</style>
