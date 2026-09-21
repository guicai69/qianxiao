import api from '@/api'
import { fetchCsv } from '@/utils/download'

export const paymentApi = {
  list(params) { return api.get('payments/', params) },
  recharge(data) { return api.post('payments/recharge/', data) },
  pay(data) { return api.post('payments/pay/', data) },
  confirmCash(data) { return api.post('payments/confirm_cash/', data) },
  exportCsv(params) { return fetchCsv('/api/payments/export_csv/', params) },
}
