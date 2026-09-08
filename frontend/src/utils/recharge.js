// 充值赠送档位 —— 与后端 payments/views.py 的 RECHARGE_BONUS_TIERS 保持一致
export const RECHARGE_BONUS_TIERS = [
  { amount: 100, bonus: 10 },
  { amount: 300, bonus: 40 },
  { amount: 500, bonus: 80 },
  { amount: 1000, bonus: 200 },
]

export function getRechargeBonus(amount) {
  let bonus = 0
  for (const t of RECHARGE_BONUS_TIERS) {
    if (Number(amount) >= t.amount) bonus = t.bonus
  }
  return bonus
}
