import request from '@/utils/request'

// request interceptor already returns response.data
// so all calls return the response body directly

export default {
  get: (url, params) => request.get(url, { params }),
  post: (url, data) => request.post(url, data),
  put: (url, data) => request.put(url, data),
  patch: (url, data) => request.patch(url, data),
  delete: (url) => request.delete(url),
}
