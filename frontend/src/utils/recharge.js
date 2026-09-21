// 充值赠送档位。后端 payments/bonus_tiers/ 是单一真源，
// 本地这份只是接口未返回时的兜底（与后端默认一致）。
import api from '@/api'

export const RECHARGE_BONUS_TIERS = [
  { amount: 100, bonus: 10 },
  { amount: 300, bonus: 40 },
  { amount: 500, bonus: 80 },
  { amount: 1000, bonus: 200 },
]

export async function loadBonusTiers() {
  try {
    const res = await api.get('payments/bonus_tiers/')
    const tiers = res?.data?.tiers
    if (Array.isArray(tiers) && tiers.length) {
      RECHARGE_BONUS_TIERS.length = 0
      tiers.forEach((t) => RECHARGE_BONUS_TIERS.push({
        amount: Number(t.amount),
        bonus: Number(t.bonus),
      }))
    }
  } catch {
    // 接口异常时保持兜底档位
  }
}

export function getRechargeBonus(amount) {
  let bonus = 0
  for (const t of RECHARGE_BONUS_TIERS) {
    if (Number(amount) >= t.amount) bonus = t.bonus
  }
  return bonus
}
