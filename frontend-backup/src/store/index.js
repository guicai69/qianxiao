import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')
  const userInfo = ref(JSON.parse(sessionStorage.getItem('user_info') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const role = computed(() => userInfo.value?.role || '')
  const isAdmin = computed(() => role.value === 'admin')
  const isReception = computed(() => role.value === 'reception')
  const isMember = computed(() => role.value === 'member')

  function setToken(access, refresh) {
    token.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  function clearToken() {
    token.value = ''
    refreshToken.value = ''
    userInfo.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    sessionStorage.removeItem('user_info')
  }

  function setUserInfo(info) {
    userInfo.value = info
    sessionStorage.setItem('user_info', JSON.stringify(info))
  }

  function hasPermission(requiredRole) {
    if (!requiredRole) return true
    if (Array.isArray(requiredRole)) return requiredRole.includes(role.value)
    return role.value === requiredRole
  }

  return {
    token, refreshToken, userInfo,
    isLoggedIn, role, isAdmin, isReception, isMember,
    setToken, clearToken, setUserInfo, hasPermission,
  }
})
