import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('vue-router', () => ({
  useRoute: () => ({ params: { id: '1' } }),
  useRouter: () => ({ push: vi.fn() }),
}))

vi.mock('@/api/venues', () => ({
  venueApi: {
    detail: vi.fn().mockResolvedValue({
      id: 1, name: '测试场馆', is_active: false, courts: [], time_slots: [],
    }),
    availability: vi.fn().mockResolvedValue({ occupied: [] }),
  },
}))
vi.mock('@/api/bookings', () => ({ bookingApi: { create: vi.fn() } }))
vi.mock('@/api/payments', () => ({ paymentApi: { pay: vi.fn() } }))

import VenueDetail from '@/views/member/VenueDetail.vue'

const stubs = {
  'el-button': { template: '<button><slot /></button>' },
  'el-icon': { template: '<i><slot /></i>' },
  'el-tag': { template: '<span><slot /></span>' },
  'el-date-picker': true,
  'el-dialog': true,
  'el-radio-group': true,
  'el-radio': true,
  'el-skeleton': true,
  // happy-dom 无法解析 /img/ 绝对路径，img 一律桩掉
  img: { props: ['alt'], template: '<img :alt="alt" />' },
}

describe('VenueDetail 场地预订页', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('停用场馆渲染提示（蓝白规范回归检查）', async () => {
    const wrapper = mount(VenueDetail, {
      global: { stubs },
    })
    await new Promise((r) => setTimeout(r, 50))
    expect(wrapper.text()).toContain('测试场馆')
    expect(wrapper.text()).toContain('已停用')
  })
})
