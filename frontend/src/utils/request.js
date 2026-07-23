import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store'

const request = axios.create({
  baseURL: '/api/',
  timeout: 10000,
})

// Request interceptor — attach JWT token
request.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor — handle common errors
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const { response } = error
    if (response) {
      switch (response.status) {
        case 401:
          ElMessage.error('登录已过期，请重新登录')
          break
        case 403:
          ElMessage.error('没有权限访问')
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        default:
          // 提取 DRF 验证错误详情
          const data = response.data
          if (typeof data === 'object') {
            const msgs = []
            for (const [key, val] of Object.entries(data)) {
              msgs.push(Array.isArray(val) ? val.join('; ') : val)
            }
            ElMessage.error(msgs.join('; ') || '请求失败')
          } else {
            ElMessage.error(response.data?.detail || response.data?.message || '请求失败')
          }
      }
    } else {
      ElMessage.error('网络连接失败')
    }
    return Promise.reject(error)
  }
)

export default request
