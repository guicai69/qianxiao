import axios from 'axios'
import api from '@/api'
import { useUserStore } from '@/store'

export const paymentApi = {
  list(params) { return api.get('payments/', params) },
  recharge(data) { return api.post('payments/recharge/', data) },
  pay(data) { return api.post('payments/pay/', data) },
  async exportCsv(params) {
    const userStore = useUserStore()
    const res = await axios.get('/api/payments/export_csv/', {
      params,
      headers: { Authorization: `Bearer ${userStore.token}` },
      responseType: 'blob',
    })
    return res.data
  },
}
