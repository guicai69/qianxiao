<template>
  <div class="not-found">
    <h1>404</h1>
    <p>页面不存在</p>
    <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
  </div>
</template>

<style scoped>
.not-found { text-align: center; padding-top: 100px; }
.not-found h1 { font-size: 72px; color: #409EFF; margin: 0; }
.not-found p { font-size: 18px; color: #999; margin: 16px 0 24px; }
</style>
