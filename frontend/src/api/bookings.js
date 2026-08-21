import axios from 'axios'
import api from '@/api'
import { useUserStore } from '@/store'

export const bookingApi = {
  list(params) { return api.get('bookings/', params) },
  create(data) { return api.post('bookings/', data) },
  detail(id) { return api.get(`bookings/${id}/`) },
  cancel(id) { return api.post(`bookings/${id}/cancel/`) },
  pay(id) { return api.post(`bookings/${id}/pay/`) },
  my(params) { return api.get('bookings/my/', params) },
  checkIn(id) { return api.post(`bookings/${id}/check_in/`) },
  async exportCsv(params) {
    const userStore = useUserStore()
    const res = await axios.get('/api/bookings/export_csv/', {
      params,
      headers: { Authorization: `Bearer ${userStore.token}` },
      responseType: 'blob',
    })
    return res.data
  },
}
