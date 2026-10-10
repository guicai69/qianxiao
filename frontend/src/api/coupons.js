import api from '@/api'

export const couponApi = {
  list(params) { return api.get('coupons/', params) },
  detail(id) { return api.get(`coupons/${id}/`) },
  create(data) { return api.post('coupons/', data) },
  update(id, data) { return api.patch(`coupons/${id}/`, data) },
  delete(id) { return api.delete(`coupons/${id}/`) },
  toggleActive(id) { return api.post(`coupons/${id}/toggle_active/`) },
  claim(id) { return api.post(`coupons/${id}/claim/`) },
  my(params) { return api.get('coupons/my/', params) },
  redeem() { return api.post('coupons/redeem/') },
}
