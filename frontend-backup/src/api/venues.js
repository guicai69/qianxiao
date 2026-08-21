import api from '@/api'

export const venueApi = {
  list(params) { return api.get('venues/', params) },
  detail(id) { return api.get(`venues/${id}/`) },
  create(data) { return api.post('venues/', data) },
  update(id, data) { return api.patch(`venues/${id}/`, data) },
  delete(id) { return api.delete(`venues/${id}/`) },
  toggleActive(id) { return api.patch(`venues/${id}/toggle_active/`, {}) },
}

export const courtApi = {
  list(params) { return api.get('courts/', params) },
  detail(id) { return api.get(`courts/${id}/`) },
  create(data) { return api.post('courts/', data) },
  update(id, data) { return api.patch(`courts/${id}/`, data) },
  delete(id) { return api.delete(`courts/${id}/`) },
  toggleActive(id) { return api.patch(`courts/${id}/toggle_active/`, {}) },
}

export const timeSlotApi = {
  list(params) { return api.get('time-slots/', params) },
  detail(id) { return api.get(`time-slots/${id}/`) },
  create(data) { return api.post('time-slots/', data) },
  update(id, data) { return api.patch(`time-slots/${id}/`, data) },
  delete(id) { return api.delete(`time-slots/${id}/`) },
  toggleActive(id) { return api.patch(`time-slots/${id}/toggle_active/`, {}) },
}
