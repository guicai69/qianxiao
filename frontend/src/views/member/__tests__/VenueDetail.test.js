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
  venueApi: { detail: vi.fn(), availability: vi.fn() },
}))
vi.mock('@/api/bookings', () => ({ bookingApi: { create: vi.fn() } }))
vi.mock('@/api/payments', () => ({ paymentApi: { pay: vi.fn() } }))
vi.mock('@/api/coupons', () => ({ couponApi: { available: vi.fn().mockResolvedValue({ results: [] }) } }))
// 只关心「有没有给出提示」，把 ElMessage 换成可断言的 spy
vi.mock('element-plus', () => ({
  ElMessage: { info: vi.fn(), success: vi.fn(), warning: vi.fn(), error: vi.fn() },
  ElMessageBox: { confirm: vi.fn() },
}))

import { venueApi } from '@/api/venues'
import { ElMessage } from 'element-plus'
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

const pad = (n) => String(n).padStart(2, '0')
const isoDay = (offset = 0) => {
  const d = new Date()
  d.setDate(d.getDate() + offset)
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}
const humanDay = (offset = 0) => {
  const d = new Date()
  d.setDate(d.getDate() + offset)
  return `${d.getMonth() + 1}月${d.getDate()}日`
}

/** 2 片场地 × 1 个时段 = 2 个可约格子；时段放到 23:59 以免受「今天已开场」规则干扰 */
const activeVenue = (over = {}) => ({
  id: 2,
  name: '测试球馆',
  is_active: true,
  courts: [{ id: 11, name: 'A场' }, { id: 12, name: 'B场' }],
  time_slots: [{ id: 21, display: '23:59-23:59', start_time: '23:59', end_time: '23:59', price: 50, is_active: true }],
  ...over,
})
const allCells = [{ court_id: 11, time_slot_id: 21 }, { court_id: 12, time_slot_id: 21 }]

async function mountVenue() {
  const wrapper = mount(VenueDetail, { global: { stubs } })
  await flushPromises()
  await new Promise((r) => setTimeout(r, 30))
  await flushPromises()
  return wrapper
}

describe('VenueDetail 场地预订页', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(ElMessage.info).mockClear()
    venueApi.detail.mockReset()
    venueApi.availability.mockReset()
    // 默认：停用场馆（第一条用例用它验证提示），需要可约场景的用例自行覆盖
    venueApi.detail.mockResolvedValue({ id: 1, name: '测试场馆', is_active: false, courts: [], time_slots: [] })
    venueApi.availability.mockResolvedValue({ occupied: [] })
  })

  it('停用场馆渲染提示（蓝白规范回归检查）', async () => {
    const wrapper = await mountVenue()
    expect(wrapper.text()).toContain('测试场馆')
    expect(wrapper.text()).toContain('已停用')
  })

  it('今天已约满时「今天」按钮禁用并标注已满，自动落到明天', async () => {
    venueApi.detail.mockResolvedValue(activeVenue({ name: '满场球馆' }))
    venueApi.availability.mockImplementation((id, params) =>
      Promise.resolve({ occupied: params.date === isoDay(0) ? allCells : [] }))

    const wrapper = await mountVenue()
    const chips = wrapper.findAll('button.quick-chip')
    expect(chips.length).toBe(2)
    expect(chips[0].attributes('disabled')).toBeDefined()
    expect(chips[0].text()).toContain('已满')
    expect(chips[1].attributes('disabled')).toBeUndefined()
    expect(chips[1].classes()).toContain('is-on')
    expect(ElMessage.info).toHaveBeenCalledWith(expect.stringContaining(humanDay(1)))
  })

  it('今天还有空位时不自动跳日期，也不会弹提示', async () => {
    venueApi.detail.mockResolvedValue(activeVenue())

    const wrapper = await mountVenue()
    const chips = wrapper.findAll('button.quick-chip')
    expect(chips[0].attributes('disabled')).toBeUndefined()
    expect(chips[0].classes()).toContain('is-on')
    expect(chips[1].classes()).not.toContain('is-on')
    expect(ElMessage.info).not.toHaveBeenCalled()
  })

  it('连续几天约满时跳到第一个有空位的日期', async () => {
    venueApi.detail.mockResolvedValue(activeVenue())
    const fullDays = [isoDay(0), isoDay(1)]
    venueApi.availability.mockImplementation((id, params) =>
      Promise.resolve({ occupied: fullDays.includes(params.date) ? allCells : [] }))

    const wrapper = await mountVenue()
    const chips = wrapper.findAll('button.quick-chip')
    // 今天、明天都满：都不选中，说明落到了更后面的日期
    expect(chips[0].classes()).toContain('is-full')
    expect(chips[1].classes()).toContain('is-full')
    expect(chips[0].classes()).not.toContain('is-on')
    expect(chips[1].classes()).not.toContain('is-on')
    expect(ElMessage.info).toHaveBeenCalledWith(expect.stringContaining(humanDay(2)))
  })
})
