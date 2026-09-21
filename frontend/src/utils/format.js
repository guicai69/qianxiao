// 统一的展示格式化工具：标签文案/颜色/金额只在里定义，页面不要手抄。
// 文案与后端 models 的 choices 保持一致（booking/payment status、payment type/method）。

export const money = (v) => Number(v || 0).toFixed(2)

export const discountText = (rate) => {
  const v = Number(rate)
  if (!v || v >= 1) return '原价'
  // PRODUCT.md §10：0.95 -> "9.5折"、0.9 -> "9折"（不是 95折）
  const d = v * 10
  return d % 1 === 0 ? `${d}折` : `${d.toFixed(1).replace(/\.0$/, '')}折`
}

export const roleLabel = (r) => ({ admin: '管理员', reception: '前台', member: '会员' }[r])
export const levelLabel = (l) => ({ normal: '普通会员', silver: '银卡会员', gold: '金卡会员' }[l] || l)

// 预约订单状态
export const bookingStatusLabel = (s) => ({ pending: '待支付', paid: '已支付', cancelled: '已取消' }[s] || s)
export const bookingStatusTag = (s) => ({ pending: 'warning', paid: 'success', cancelled: 'info' }[s] || 'info')

// 支付记录状态 / 类型 / 方式
export const paymentStatusLabel = (s) => ({ success: '成功', failed: '失败', pending: '处理中' }[s] || s)
export const paymentStatusTag = (s) => ({ success: 'success', failed: 'danger', pending: 'info' }[s] || 'info')
export const paymentTypeLabel = (t) => ({ recharge: '充值', booking: '消费', refund: '退款' }[t] || t)
export const paymentTypeTag = (t) => ({ recharge: 'success', booking: 'primary', refund: 'warning' }[t] || 'info')
export const paymentMethodLabel = (m) =>
  ({ balance: '余额', wechat: '微信', alipay: '支付宝', cash: '现金' }[m] || '其他')
