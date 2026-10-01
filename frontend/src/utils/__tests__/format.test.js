import { describe, it, expect } from 'vitest'
import {
  money,
  discountText,
  bookingStatusLabel,
  bookingStatusTag,
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

  it('payment 状态与类型', () => {
    expect(paymentStatusLabel('success')).toBe('成功')
    expect(paymentStatusLabel('failed')).toBe('失败')
    expect(paymentTypeTag('booking')).toBe('primary')
    expect(paymentTypeTag('refund')).toBe('warning')
  })
})
