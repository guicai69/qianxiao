import { describe, it, expect, vi, beforeEach } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('@/api', () => ({
  default: { get: vi.fn().mockResolvedValue({ data: { balance: '100.00' } }) },
}))
vi.mock('@/api/bookings', () => ({
  bookingApi: { my: vi.fn(), cancel: vi.fn(), requestCancel: vi.fn() },
}))
vi.mock('@/api/payments', () => ({
  paymentApi: { pay: vi.fn(), recharge: vi.fn() },
}))
vi.mock('@/api/reviews', () => ({ reviewApi: { create: vi.fn() } }))
vi.mock('element-plus', () => ({
  ElMessage: { info: vi.fn(), success: vi.fn(), warning: vi.fn(), error: vi.fn() },
  ElMessageBox: { confirm: vi.fn() },
}))

import { bookingApi } from '@/api/bookings'
import MemberOrders from '@/views/member/MemberOrders.vue'

const stubs = {
  'el-button': { template: '<button><slot /></button>' },
  'el-icon': { template: '<i><slot /></i>' },
  'el-tag': { template: '<span><slot /></span>' },
  'el-radio-group': { template: '<div><slot /></div>' },
  'el-radio-button': { template: '<span><slot /></span>' },
  'el-radio': { template: '<span><slot /></span>' },
  'el-skeleton': true,
  'el-pagination': true,
  // 弹窗内容不参与断言，直接吞掉，免得「确认支付」之类文案干扰按钮断言
  'el-dialog': { template: '<div />' },
}

const baseRow = (over = {}) => ({
  id: 1,
  venue_name: '天河体育中心羽毛球馆',
  court_name: '1号场',
  date: '2026-10-22',
  time_slot_display: '10:00-11:00',
  amount: '100.00',
  status: 'paid',
  checked_in: false,
  cancel_window: 'free',
  cancellation_status: null,
  is_finished: false,
  is_expired: false,
  ...over,
})

async function mountWith(rows) {
  bookingApi.my.mockResolvedValue({ results: rows, count: rows.length })
  const wrapper = mount(MemberOrders, { global: { stubs } })
  await flushPromises()
  return wrapper
}

const buttonTexts = (wrapper) => wrapper.findAll('button').map((b) => b.text())

describe('MemberOrders 我的订单', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    bookingApi.my.mockReset()
  })

  it('已支付但时段已结束：显示「已结束」，不再提供任何操作入口', async () => {
    const wrapper = await mountWith([baseRow({ is_finished: true, cancel_window: 'ended' })])
    const text = wrapper.text()

    expect(text).toContain('已结束')
    expect(text).toContain('时段已结束')
    expect(text).not.toContain('待使用')
    expect(buttonTexts(wrapper)).not.toContain('支付')
    expect(buttonTexts(wrapper)).not.toContain('取消预约')
    expect(buttonTexts(wrapper)).not.toContain('申请退场')
    expect(buttonTexts(wrapper)).not.toContain('评价')
  })

  it('待支付但已超时：显示「已结束」和超时说明，不再展示支付/取消', async () => {
    const wrapper = await mountWith([
      baseRow({ status: 'pending', is_expired: true, cancel_window: null }),
    ])
    const text = wrapper.text()

    expect(text).toContain('已结束')
    expect(text).toContain('超时未支付，订单已结束')
    expect(buttonTexts(wrapper)).not.toContain('支付')
    expect(buttonTexts(wrapper)).not.toContain('取消')
  })

  it('待支付且未超时：照常显示支付与取消', async () => {
    const wrapper = await mountWith([baseRow({ status: 'pending', cancel_window: null })])
    const text = wrapper.text()

    expect(text).toContain('待支付')
    expect(text).not.toContain('已结束')
    expect(buttonTexts(wrapper)).toContain('支付')
    expect(buttonTexts(wrapper)).toContain('取消')
  })

  it('已支付未结束：显示「待使用」并保留取消/退场入口', async () => {
    const wrapper = await mountWith([baseRow()])
    const text = wrapper.text()

    expect(text).toContain('已支付')
    expect(text).toContain('待使用')
    expect(text).not.toContain('已结束')
    expect(buttonTexts(wrapper)).toContain('取消预约')
  })

  it('已开场进入退场审批窗口：显示「申请退场」', async () => {
    const wrapper = await mountWith([baseRow({ cancel_window: 'started' })])
    expect(buttonTexts(wrapper)).toContain('申请退场')
    expect(buttonTexts(wrapper)).not.toContain('取消预约')
  })

  it('已签到订单可评价，且不再显示「待使用」', async () => {
    const wrapper = await mountWith([baseRow({ checked_in: true })])
    const text = wrapper.text()

    expect(text).toContain('已签到')
    expect(text).not.toContain('待使用')
    expect(buttonTexts(wrapper)).toContain('评价')
  })

  it('没有订单时展示空状态', async () => {
    const wrapper = await mountWith([])
    expect(wrapper.text()).toContain('还没有这类订单')
  })
})
