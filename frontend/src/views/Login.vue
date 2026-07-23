<template>
  <div class="login-page">
    <el-card class="login-card">
      <h2>🏸 羽毛球馆管理系统</h2>
      <el-form :model="form" label-width="80px">
        <el-form-item label="手机号">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" style="width:100%" @click="handleLogin">登 录</el-button>
        </el-form-item>
        <el-form-item>
          <el-button link type="primary" @click="$router.push('/register')">还没有账号？立即注册</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive } from 'vue'

const form = reactive({ phone: '', password: '' })

function handleLogin() {
  // Will be implemented in phase 2
}
</script>

<style scoped>
.login-page { display: flex; align-items: center; justify-content: center; height: 100vh; background: #f0f2f5; }
.login-card { width: 400px; }
.login-card h2 { text-align: center; margin-bottom: 24px; }
</style>
