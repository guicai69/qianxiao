import { describe, it, expect, vi, beforeEach } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('vue-router', () => ({
  useRoute: () => ({ params: { id: '1' } }),
  useRouter: () => ({ push: vi.fn() }),
  createRouter: vi.fn(() => ({ beforeEach: vi.fn(), afterEach: vi.fn(), onError: vi.fn() })),
  createWebHistory: vi.fn(() => ({})),
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

  it('今天已约满时「今天」按钮禁用并标注已满', async () => {
    const { venueApi } = await import('@/api/venues')
    const d = new Date()
    const todayStr = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    // 2 片场地 × 1 个时段 = 2 个格子，今天这两个格子都被占满
    venueApi.detail.mockResolvedValueOnce({
      id: 2,
      name: '满场球馆',
      is_active: true,
      courts: [{ id: 11, name: 'A场' }, { id: 12, name: 'B场' }],
      time_slots: [{ id: 21, display: '23:00-23:59', start_time: '23:00', price: 50, is_active: true }],
    })
    venueApi.availability.mockImplementation((id, params) => Promise.resolve({
      occupied: params.date === todayStr
        ? [{ court_id: 11, time_slot_id: 21 }, { court_id: 12, time_slot_id: 21 }]
        : [],
    }))

    const wrapper = mount(VenueDetail, { global: { stubs } })
    await flushPromises()
    await new Promise((r) => setTimeout(r, 30))
    await flushPromises()

    const chips = wrapper.findAll('button.quick-chip')
    expect(chips.length).toBe(2)
    expect(chips[0].attributes('disabled')).toBeDefined()
    expect(chips[0].text()).toContain('已满')
    expect(chips[1].attributes('disabled')).toBeUndefined()
  })
})
