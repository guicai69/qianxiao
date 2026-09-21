import api from '@/api'
import { fetchCsv } from '@/utils/download'

export const bookingApi = {
  list(params) { return api.get('bookings/', params) },
  create(data) { return api.post('bookings/', data) },
  detail(id) { return api.get(`bookings/${id}/`) },
  cancel(id) { return api.post(`bookings/${id}/cancel/`) },
  my(params) { return api.get('bookings/my/', params) },
  checkIn(id) { return api.post(`bookings/${id}/check_in/`) },
  exportCsv(params) { return fetchCsv('/api/bookings/export_csv/', params) },
}
