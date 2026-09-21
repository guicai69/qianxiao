import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

import App from './App.vue'
import router from './router'
import 'nprogress/nprogress.css'
import './style.css'

const app = createApp(App)

// 图标一律在组件内按需 import（全局注册会拖垮 tree-shaking，打包体积翻倍）
app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })
app.mount('#app')

