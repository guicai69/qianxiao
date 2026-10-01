import api from '@/api'

export const activityApi = {
  list(params) { return api.get('activities/', params) },
  register(id) { return api.post(`activities/${id}/register/`) },
  cancel(id) { return api.post(`activities/${id}/cancel/`) },
  my() { return api.get('activities/my/') },
}
