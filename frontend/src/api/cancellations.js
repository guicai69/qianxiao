import api from '@/api'

export const cancellationApi = {
  list(params) { return api.get('cancellation-requests/', params) },
  approve(id) { return api.post(`cancellation-requests/${id}/approve/`) },
  reject(id, data) { return api.post(`cancellation-requests/${id}/reject/`, data || {}) },
}
