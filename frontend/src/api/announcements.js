import api from '@/api'

export const announcementApi = {
  list(params) { return api.get('announcements/', params) },
  create(data) { return api.post('announcements/', data) },
  update(id, data) { return api.patch(`announcements/${id}/`, data) },
  delete(id) { return api.delete(`announcements/${id}/`) },
  togglePublish(id) { return api.post(`announcements/${id}/toggle_publish/`) },
  togglePin(id) { return api.post(`announcements/${id}/toggle_pin/`) },
}
