import api from '@/api'

export const couponApi = {
  list(params) { return api.get('coupons/', params) },
  claim(id) { return api.post(`coupons/${id}/claim/`) },
  my(params) { return api.get('coupons/my/', params) },
  redeem() { return api.post('coupons/redeem/') },
}
