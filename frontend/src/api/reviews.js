import api from '@/api'

export const reviewApi = {
  list(params) { return api.get('reviews/', params) },
  create(data) { return api.post('reviews/', data) },
}

export const favoriteApi = {
  list() { return api.get('favorites/') },
  add(venueId) { return api.post('favorites/', { venue: venueId }) },
  remove(id) { return api.delete(`favorites/${id}/`) },
}

export const feedbackApi = {
  create(data) { return api.post('feedbacks/', data) },
}
