import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store'
import router from '@/router'

const request = axios.create({
  baseURL: '/api/',
  timeout: 10000,
})

// —— token 刷新（单飞：并发 401 只触发一次刷新）——
let isRefreshing = false
let pendingQueue = []

function flushQueue(error, token = null) {
  pendingQueue.forEach((cb) => cb(error, token))
  pendingQueue = []
}

function handleLogout() {
  const userStore = useUserStore()
  const hadSession = !!userStore.token || !!userStore.userInfo
  userStore.clearToken()
  if (hadSession) ElMessage.error('登录已过期，请重新登录')
  if (router.currentRoute.value.path !== '/login') {
    router.replace('/login')
  }
}

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

// Response interceptor — 401 自动刷新 token，失败则自动登出
request.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const { response, config } = error
    const userStore = useUserStore()

    // 401 且尚未重试过、且有 refresh token → 尝试静默续期
    if (response?.status === 401 && config && !config._retry && userStore.refreshToken) {
      if (isRefreshing) {
        // 等待正在进行的刷新完成
        return new Promise((resolve, reject) => {
          pendingQueue.push((refreshError, newToken) => {
            if (refreshError) return reject(refreshError)
            config._retry = true
            config.headers.Authorization = `Bearer ${newToken}`
            resolve(request(config))
          })
        })
      }

      config._retry = true
      isRefreshing = true
      try {
        const res = await axios.post('/api/auth/token/refresh/', {
          refresh: userStore.refreshToken,
        })
        const newAccess = res.data.access
        const newRefresh = res.data.refresh || userStore.refreshToken
        userStore.setToken(newAccess, newRefresh)
        flushQueue(null, newAccess)
        config.headers.Authorization = `Bearer ${newAccess}`
        return request(config)
      } catch (refreshError) {
        flushQueue(refreshError, null)
        handleLogout()
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    if (response) {
      switch (response.status) {
        case 401:
          handleLogout()
          break
        case 403:
          ElMessage.error('没有权限访问')
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        default: {
          const data = response.data
          if (data && typeof data === 'object') {
            const msgs = []
            for (const [key, val] of Object.entries(data)) {
              if (key === 'detail') continue
              msgs.push(Array.isArray(val) ? val.join('; ') : val)
            }
            if (msgs.length) {
              ElMessage.error(msgs.join('; '))
            } else {
              ElMessage.error(data.detail || data.message || '请求失败')
            }
          } else {
            ElMessage.error(data?.detail || data?.message || '请求失败')
          }
        }
      }
    } else {
      ElMessage.error('网络连接失败')
    }
    return Promise.reject(error)
  }
)

export default request
