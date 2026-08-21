import api from '@/api'

export const statsApi = {
  overview() { return api.get('stats/overview/') },
  revenueTrend(days) { return api.get('stats/revenue_trend/', { days }) },
  courtUsage() { return api.get('stats/court_usage/') },
  popularSlots() { return api.get('stats/popular_slots/') },
}
