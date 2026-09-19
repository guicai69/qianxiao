/* finesse · register=product · A=amber-on-ink-green · B=800/300 + mono numerals
 * C=rail shell + hairline bands · D=ECharts token theme · E=paper/hairline
 * SOUL=5 SPECTACLE=2 DENSITY=8
 *
 * 看板图表的统一配色层：ECharts 不认识 CSS 变量，所以在这里把令牌读成值，
 * 两个看板（admin / reception）共用，避免各自内联一套十六进制。
 */

const css = getComputedStyle(document.documentElement)
const tok = (name, fb) => (css.getPropertyValue(name) || '').trim() || fb

export const CHART_COLORS = [
  tok('--accent', '#a85a1e'),
  tok('--accent-2', '#2f6b4f'),
  tok('--info', '#2c6b8c'),
  tok('--warn', '#b77a16'),
  tok('--ink-3', '#6e7d74'),
]

export const CHART_AXIS = {
  axisLine: { show: false },
  axisTick: { show: false },
  axisLabel: { color: tok('--ink-3', '#6e7d74'), fontSize: 11 },
  splitLine: { lineStyle: { color: tok('--border-soft', 'rgba(20,32,26,.06)') } },
}

export const CHART_TOOLTIP = {
  backgroundColor: tok('--surface', '#fbfcf9'),
  borderColor: tok('--border', 'rgba(20,32,26,.09)'),
  borderWidth: 1,
  textStyle: { color: tok('--ink-1', '#14201a'), fontSize: 12 },
  extraCssText: 'border-radius:10px;box-shadow:0 8px 24px -10px rgba(20,40,30,.25)',
}

export const CHART_LEGEND = {
  textStyle: { color: tok('--ink-3', '#6e7d74'), fontSize: 11 },
  itemWidth: 12,
  itemHeight: 8,
  itemGap: 16,
  icon: 'roundRect',
}

/* 减少动态效果：尊重系统设置，图表只给终态 */
export const RM = matchMedia('(prefers-reduced-motion: reduce)').matches

/* 图表统一：有数据才画，空数据不画一具空骨架 */
export const CHART_ANIMATION = !RM

const HEX = /^#([0-9a-f]{3}|[0-9a-f]{6})$/i

/** 把令牌色转成带透明度的 rgba；非十六进制（已是 rgba() 的令牌）原样返回 */
export function alpha(color, a) {
  const value = String(color || '').trim()
  if (!HEX.test(value)) return value
  let hex = value.slice(1)
  if (hex.length === 3) hex = hex.split('').map((c) => c + c).join('')
  const n = parseInt(hex, 16)
  return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${a})`
}

/** 每次返回一份新的坐标轴配置，避免多个图表共享同一对象 */
export function chartAxis(extra = {}) {
  const { axisLabel, splitLine, ...rest } = extra
  return {
    axisLine: { show: false },
    axisTick: { show: false },
    ...rest,
    axisLabel: { ...CHART_AXIS.axisLabel, ...(axisLabel || {}) },
    splitLine: { lineStyle: { ...CHART_AXIS.splitLine.lineStyle }, ...(splitLine || {}) },
  }
}

export function chartTooltip(extra = {}) {
  return { ...CHART_TOOLTIP, textStyle: { ...CHART_TOOLTIP.textStyle }, ...extra }
}

export function chartLegend(extra = {}) {
  return { ...CHART_LEGEND, textStyle: { ...CHART_LEGEND.textStyle }, ...extra }
}
