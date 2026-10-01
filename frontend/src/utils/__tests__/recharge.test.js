import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('@/api', () => ({
  default: { get: vi.fn() },
}))

import api from '@/api'
import { RECHARGE_BONUS_TIERS, getRechargeBonus, loadBonusTiers } from '@/utils/recharge'

describe('utils/recharge', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    RECHARGE_BONUS_TIERS.length = 0
    RECHARGE_BONUS_TIERS.push(
      { amount: 100, bonus: 10 },
      { amount: 300, bonus: 40 },
      { amount: 500, bonus: 80 },
      { amount: 1000, bonus: 200 },
    )
  })

  it('兜底档位取最高档', () => {
    expect(getRechargeBonus(0)).toBe(0)
    expect(getRechargeBonus(100)).toBe(10)
    expect(getRechargeBonus(300)).toBe(40)
    expect(getRechargeBonus(1000)).toBe(200)
  })

  it('接口档位覆盖兜底（单一真源）', async () => {
    api.get.mockResolvedValue({
      data: { tiers: [{ amount: '100', bonus: '5' }, { amount: '200', bonus: '15' }] },
    })
    await loadBonusTiers()
    expect(getRechargeBonus(100)).toBe(5)
    expect(getRechargeBonus(200)).toBe(15)
  })

  it('接口异常保持兜底档位', async () => {
    api.get.mockRejectedValue(new Error('network'))
    await loadBonusTiers()
    expect(getRechargeBonus(300)).toBe(40)
  })
})
