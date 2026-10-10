import api from '@/api'

export const activityApi = {
  list(params) { return api.get('activities/', params) },
  detail(id) { return api.get(`activities/${id}/`) },
  create(data) { return api.post('activities/', data) },
  update(id, data) { return api.patch(`activities/${id}/`, data) },
  delete(id) { return api.delete(`activities/${id}/`) },
  toggleActive(id) { return api.post(`activities/${id}/toggle_active/`) },
  registrations(id) { return api.get(`activities/${id}/registrations/`) },
  attend(id, registrationId) { return api.post(`activities/${id}/attend/`, { registration_id: registrationId }) },
  register(id) { return api.post(`activities/${id}/register/`) },
  cancel(id) { return api.post(`activities/${id}/cancel/`) },
  my() { return api.get('activities/my/') },
}
