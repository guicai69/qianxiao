import request from '@/utils/request'

// Will be extended per module in later phases
export default {
  // Auth
  login: (data) => request.post('auth/login/', data),
  register: (data) => request.post('auth/register/', data),
  refreshToken: (data) => request.post('auth/token/refresh/', data),

  // Generic helpers
  get: (url, params) => request.get(url, { params }),
  post: (url, data) => request.post(url, data),
  put: (url, data) => request.put(url, data),
  patch: (url, data) => request.patch(url, data),
  delete: (url) => request.delete(url),
}
