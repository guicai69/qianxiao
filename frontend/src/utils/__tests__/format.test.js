import { describe, it, expect } from 'vitest'
import {
  money,
  discountText,
  bookingStatusLabel,
  bookingStatusTag,
  orderClosed,
  orderStateLabel,
  orderStateTag,
  paymentStatusLabel,
  paymentTypeTag,
} from '@/utils/format'

describe('utils/format', () => {
  it('money 两位小数', () => {
    expect(money(0)).toBe('0.00')
    expect(money('88')).toBe('88.00')
    expect(money(undefined)).toBe('0.00')
  })

  it('discountText 9.5折口径（PRODUCT §10）', () => {
    expect(discountText(1)).toBe('原价')
    expect(discountText(0.95)).toBe('9.5折')
    expect(discountText(0.9)).toBe('9折')
    expect(discountText(0)).toBe('原价')
  })

  it('booking 状态文案与颜色', () => {
    expect(bookingStatusLabel('pending')).toBe('待支付')
    expect(bookingStatusTag('paid')).toBe('success')
    expect(bookingStatusTag('cancelled')).toBe('info')
    expect(bookingStatusTag('unknown')).toBe('info')
  })

  it('订单「视为结束」：已支付且时段已过 / 待支付且超时未付', () => {
    expect(orderClosed({ status: 'paid', is_finished: true })).toBe(true)
    expect(orderClosed({ status: 'pending', is_expired: true })).toBe(true)
    expect(orderClosed({ status: 'paid', is_finished: false })).toBe(false)
    expect(orderStateLabel({ status: 'paid', is_finished: true })).toBe('已结束')
    expect(orderStateLabel({ status: 'pending', is_expired: true })).toBe('已结束')
    expect(orderStateLabel({ status: 'paid' })).toBe('已支付')
    expect(orderStateTag({ status: 'paid', is_finished: true })).toBe('info')
    expect(orderStateTag({ status: 'pending' })).toBe('warning')
  })

  it('payment 状态与类型', () => {
    expect(paymentStatusLabel('success')).toBe('成功')
    expect(paymentStatusLabel('failed')).toBe('失败')
    expect(paymentTypeTag('booking')).toBe('primary')
    expect(paymentTypeTag('refund')).toBe('warning')
  })
})
