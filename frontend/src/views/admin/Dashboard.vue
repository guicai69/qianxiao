<template>
  <div class="dashboard-page">
    <div class="page-header">
      <h2>经营概况</h2>
      <p>今日营收与预约、场馆场地存量，统计接口实时汇总</p>
    </div>

    <!-- 一层：四个主指标磁贴 -->
    <section class="kpi-row">
      <article v-for="(tile, i) in primaryTiles" :key="tile.label" class="kpi">
        <span class="kpi__icon" aria-hidden="true">
          <el-icon :size="12"><component :is="tile.icon" /></el-icon>
        </span>
        <span class="kpi__label">{{ tile.label }}</span>
        <strong
          class="kpi__num mono"
          :class="{ 'count-up': ready }"
          :style="{ '--i': String(i) }"
        >
          <small v-if="tile.prefix">{{ tile.prefix }}</small>{{ tile.value }}
        </strong>
        <span class="kpi__ctx" :class="{ 'is-accent': tile.accent }">{{ tile.ctx }}</span>
      </article>
    </section>

    <!-- 二层：次要指标用发丝线规格带，不再是卡片 -->
    <section class="spec-band">
      <div v-for="(item, i) in secondarySpecs" :key="item.label" class="spec">
        <div
          class="spec__num"
          :class="{ 'count-up': ready }"
          :style="{ '--i': String(i + 4) }"
        >
          {{ item.value }}
        </div>
        <div class="spec__label">{{ item.label }}</div>
      </div>
    </section>

    <!-- 图表：两张并排，趋势图通栏 -->
    <section class="chart-grid">
      <article class="panel">
        <header class="panel__head">
          <h3>各场馆场地数</h3>
          <span class="caps">按场馆</span>
        </header>
        <div class="chart-shell">
          <div ref="barChartRef" class="chart-box"></div>
          <p v-if="ready && !venues.length" class="chart-empty">暂无场馆数据</p>
        </div>
      </article>

      <article class="panel">
        <header class="panel__head">
          <h3>场馆状态分布</h3>
          <span class="caps">当前</span>
        </header>
        <div class="chart-shell">
          <div ref="pieChartRef" class="chart-box"></div>
          <p v-if="ready && !venues.length" class="chart-empty">暂无场馆数据</p>
        </div>
      </article>

      <article class="panel panel--wide">
        <header class="panel__head">
          <h3>近 7 日营收趋势</h3>
          <span class="caps">已支付订单</span>
        </header>
        <div class="chart-shell">
          <div ref="lineChartRef" class="chart-box"></div>
          <p v-if="ready && !trendData.length" class="chart-empty">近 7 日暂无营收记录</p>
        </div>
      </article>

      <article class="panel panel--wide">
        <header class="panel__head">
          <h3>热门时段 Top</h3>
          <span class="caps">预约量</span>
        </header>
        <div class="chart-shell">
          <div ref="slotsChartRef" class="chart-box chart-box--short"></div>
          <p v-if="ready && !slotsData.length" class="chart-empty">暂无时段数据</p>
        </div>
      </article>
    </section>

    <article class="panel">
      <header class="panel__head">
        <h3>场馆列表</h3>
        <el-button link type="primary" @click="$router.push('/admin/venues')">查看全部</el-button>
      </header>
      <el-table :data="venues" v-loading="loading" size="default">
        <el-table-column prop="name" label="场馆名称" min-width="160" />
        <el-table-column prop="address" label="地址" min-width="220" show-overflow-tooltip />
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" effect="light" round>
              {{ row.is_active ? "启用" : "停用" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="court_count" label="场地数" width="90" align="center" />
        <el-table-column label="操作" width="110" align="right">
          <template #default>
            <el-button size="small" @click="$router.push('/admin/venues')">管理</el-button>
          </template>
        </el-table-column>
      </el-table>
    </article>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from "vue"
import * as echarts from "echarts"
import { venueApi } from "@/api/venues"
import api from "@/api"
import { statsApi } from "@/api/stats"
import { money } from "@/utils/format"
import { Money, Calendar, TrendCharts, Warning } from "@element-plus/icons-vue"
import {
  CHART_COLORS,
  CHART_ANIMATION,
  alpha,
  chartAxis,
  chartTooltip,
  chartLegend,
} from "@/utils/chartTheme"

const barChartRef = ref(null)
const pieChartRef = ref(null)
const lineChartRef = ref(null)
const slotsChartRef = ref(null)
const venues = ref([])
const loading = ref(true)
const ready = ref(false)
const totalCourts = ref(0)
const statsData = ref(null)
const trendData = ref([])
const slotsData = ref([])
let barChart = null
let pieChart = null
let lineChart = null
let slotsChart = null

/* 一层：四个主指标，上下文一行全部来自统计接口的真实字段 */
const primaryTiles = computed(() => {
  const s = statsData.value || {}
  const paid = Number(s.today_paid || 0)
  const pending = Number(s.today_pending || 0)
  const todayRevenue = Number(s.today_revenue || 0)
  return [
    {
      label: "今日营收",
      prefix: "¥",
      value: money(todayRevenue),
      icon: Money,
      ctx: paid > 0 ? `已收款 ${paid} 笔` : "今日暂无收款",
      accent: paid > 0,
    },
    {
      label: "今日预约",
      prefix: "",
      value: String(s.today_bookings || 0),
      icon: Calendar,
      ctx: pending > 0 ? `其中 ${pending} 笔待处理` : "暂无待处理",
      accent: pending > 0,
    },
    {
      label: "累计营收",
      prefix: "¥",
      value: money(s.total_revenue),
      icon: TrendCharts,
      ctx: `充值累计 ¥${money(s.total_recharge)}`,
      accent: false,
    },
    {
      label: "待处理",
      prefix: "",
      value: String(pending),
      icon: Warning,
      ctx: pending > 0 ? "需前台收款核销" : "当前无待办",
      accent: pending > 0,
    },
  ]
})

/* 二层：次要指标，发丝线分隔的一行数字，不是卡片 */
const secondarySpecs = computed(() => {
  const s = statsData.value || {}
  return [
    { label: "场馆总数", value: String(s.total_venues || venues.value.length || 0) },
    { label: "场地总数", value: String(s.total_courts || totalCourts.value || 0) },
    { label: "会员总数", value: String(s.total_members || 0) },
    { label: "充值总额", value: `¥${money(s.total_recharge)}` },
    { label: "赠送总额", value: `¥${money(s.total_bonus)}` },
    { label: "退款总额", value: `¥${money(s.total_refund)}` },
  ]
})

async function fetchData() {
  loading.value = true
  try {
    const [vRes, cRes, stRes, trendRes, slotsRes] = await Promise.all([
      venueApi.list({ page_size: 100 }),
      api.get("courts/", { page_size: 1 }),
      statsApi.overview(),
      statsApi.revenueTrend(7),
      statsApi.popularSlots(),
    ])
    venues.value = vRes.results || []
    totalCourts.value = cRes?.count || 0
    statsData.value = stRes
    trendData.value = trendRes?.days || []
    slotsData.value = slotsRes?.slots || []
  } catch (e) {
    console.warn("Dashboard data fetch failed:", e)
  } finally {
    loading.value = false
    ready.value = true
    nextTick(initCharts)
  }
}

function initCharts() {
  if (!barChartRef.value || !pieChartRef.value || venues.value.length === 0) return

  barChart = echarts.init(barChartRef.value)
  barChart.setOption({
    animation: CHART_ANIMATION,
    tooltip: chartTooltip({ trigger: "axis", axisPointer: { type: "shadow" } }),
    grid: { left: 4, right: 12, top: 20, bottom: 4, containLabel: true },
    xAxis: chartAxis({
      type: "category",
      data: venues.value.map((v) => v.name),
      axisLabel: { interval: 0, width: 62, overflow: "truncate" },
      splitLine: { show: false },
    }),
    yAxis: chartAxis({ type: "value", minInterval: 1 }),
    series: [
      {
        type: "bar",
        data: venues.value.map((v) => v.court_count || 0),
        barWidth: 22,
        barMaxWidth: 34,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: CHART_COLORS[0] },
            { offset: 1, color: alpha(CHART_COLORS[0], 0.55) },
          ]),
          borderRadius: [5, 5, 0, 0],
        },
      },
    ],
  })

  const active = venues.value.filter((v) => v.is_active).length
  const inactive = venues.value.length - active
  pieChart = echarts.init(pieChartRef.value)
  pieChart.setOption({
    animation: CHART_ANIMATION,
    tooltip: chartTooltip({ trigger: "item", formatter: "{b}: {c} ({d}%)" }),
    legend: chartLegend({ bottom: 0, left: "center" }),
    series: [
      {
        type: "pie",
        radius: ["46%", "68%"],
        center: ["50%", "44%"],
        itemStyle: { borderRadius: 8, borderWidth: 0 },
        data: [
          { value: active, name: "已启用", itemStyle: { color: CHART_COLORS[1] } },
          { value: inactive, name: "已停用", itemStyle: { color: CHART_COLORS[4] } },
        ],
        label: {
          show: true,
          formatter: (p) => (p.value > 0 ? `${p.name}\n${p.value} 座` : ""),
          fontSize: 12,
          lineHeight: 16,
          color: CHART_COLORS[4],
        },
        labelLine: { show: true, lineStyle: { color: alpha(CHART_COLORS[4], 0.45) } },
        emphasis: {
          scaleSize: 6,
          itemStyle: { shadowBlur: 14, shadowColor: alpha(CHART_COLORS[4], 0.28) },
        },
      },
    ],
  })

  initTrendChart()
  initSlotsChart()
}

function initTrendChart() {
  if (!lineChartRef.value) return
  lineChart = echarts.init(lineChartRef.value)
  const dates = trendData.value.map((d) => String(d.date).slice(5))
  const revenues = trendData.value.map((d) => Number(d.revenue || 0))
  const bookings = trendData.value.map((d) => d.bookings || 0)

  lineChart.setOption({
    animation: CHART_ANIMATION,
    tooltip: chartTooltip({
      trigger: "axis",
      formatter: (params) => {
        const idx = params?.[0]?.dataIndex ?? 0
        const rev = revenues[idx] ?? 0
        const bk = bookings[idx] ?? 0
        return `${dates[idx]}<br/>营收：¥${rev.toFixed(2)}<br/>订单：${bk} 笔`
      },
    }),
    legend: chartLegend({ top: 0, left: 0, data: ["营收 (¥)", "订单数 (笔)"] }),
    grid: { left: 4, right: 16, top: 40, bottom: 4, containLabel: true },
    xAxis: chartAxis({
      type: "category",
      boundaryGap: false,
      data: dates,
      splitLine: { show: false },
    }),
    yAxis: [
      chartAxis({ type: "value" }),
      chartAxis({ type: "value", minInterval: 1, splitLine: { show: false } }),
    ],
    series: [
      {
        name: "营收 (¥)",
        type: "line",
        smooth: true,
        data: revenues,
        symbol: "circle",
        symbolSize: 7,
        lineStyle: { width: 2.5, color: CHART_COLORS[0] },
        itemStyle: { color: CHART_COLORS[0] },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: alpha(CHART_COLORS[0], 0.2) },
            { offset: 1, color: alpha(CHART_COLORS[0], 0.02) },
          ]),
        },
      },
      {
        name: "订单数 (笔)",
        type: "bar",
        yAxisIndex: 1,
        data: bookings,
        barWidth: 10,
        itemStyle: { color: alpha(CHART_COLORS[2], 0.75), borderRadius: [3, 3, 0, 0] },
      },
    ],
  })
}

function initSlotsChart() {
  if (!slotsChartRef.value) return
  slotsChart = echarts.init(slotsChartRef.value)
  const labels = slotsData.value.map((s) => s.label).reverse()
  const counts = slotsData.value.map((s) => s.count).reverse()

  slotsChart.setOption({
    animation: CHART_ANIMATION,
    tooltip: chartTooltip({ trigger: "axis", axisPointer: { type: "shadow" } }),
    grid: { left: 4, right: 24, top: 12, bottom: 4, containLabel: true },
    xAxis: chartAxis({ type: "value", minInterval: 1 }),
    yAxis: chartAxis({
      type: "category",
      data: labels,
      axisLabel: { color: CHART_COLORS[4], fontSize: 12 },
      splitLine: { show: false },
    }),
    series: [
      {
        type: "bar",
        data: counts,
        barWidth: 14,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: alpha(CHART_COLORS[1], 0.7) },
            { offset: 1, color: CHART_COLORS[1] },
          ]),
          borderRadius: [0, 5, 5, 0],
        },
        label: {
          show: true,
          position: "right",
          color: CHART_COLORS[1],
          fontWeight: 700,
          fontSize: 12,
        },
      },
    ],
  })
}

function handleResize() {
  barChart?.resize()
  pieChart?.resize()
  lineChart?.resize()
  slotsChart?.resize()
}

onMounted(() => {
  fetchData()
  window.addEventListener("resize", handleResize)
})

onUnmounted(() => {
  barChart?.dispose()
  pieChart?.dispose()
  lineChart?.dispose()
  slotsChart?.dispose()
  window.removeEventListener("resize", handleResize)
})
</script>

<style scoped>
.dashboard-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
  min-width: 0;
}

/* ---------- 一层：主指标磁贴 ---------- */

.kpi-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.kpi {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 7px;
  min-width: 0;
  padding: 16px 18px 18px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}

.kpi__icon {
  position: absolute;
  top: 14px;
  right: 14px;
  display: inline-flex;
  color: var(--ink-4);
  opacity: 0.55;
}

.kpi__label {
  font-size: var(--fs-12);
  font-weight: 600;
  color: var(--ink-3);
  padding-right: 20px;
}

.kpi__num {
  font-size: var(--fs-28);
  font-weight: 700;
  line-height: 1.05;
  letter-spacing: -0.02em;
  color: var(--ink-1);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.kpi__num small {
  font-size: 0.56em;
  font-weight: 600;
  color: var(--ink-3);
  margin-right: 2px;
  letter-spacing: 0;
}

.kpi__ctx {
  font-size: var(--fs-12);
  color: var(--ink-4);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.kpi__ctx.is-accent {
  color: var(--accent);
  font-weight: 600;
}

/* ---------- 二层：规格带，发丝线分隔 ---------- */

.spec-band {
  background: transparent;
}

.spec-band .spec {
  padding: 18px 20px;
}

.spec-band .spec__num {
  font-size: var(--fs-22);
}

/* ---------- 图表 ---------- */

.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.panel {
  display: flex;
  flex-direction: column;
  min-width: 0;
  padding: 18px 20px 20px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}

.panel--wide {
  grid-column: 1 / -1;
}

.panel__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
  min-width: 0;
}

.panel__head h3 {
  margin: 0;
  font-size: var(--fs-14);
  font-weight: 700;
  color: var(--ink-1);
  min-width: 0;
}

.chart-shell {
  position: relative;
  min-width: 0;
}

.chart-box {
  height: 300px;
}

.chart-box--short {
  height: 200px;
}

.chart-empty {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0;
  border-radius: var(--radius-sm);
  background: var(--surface);
  color: var(--ink-3);
  font-size: var(--fs-13);
}

/* ---------- 断点 ---------- */

@media (max-width: 1100px) {
  .kpi-row {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 820px) {
  .chart-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .panel--wide {
    grid-column: auto;
  }

  .chart-box {
    height: 240px;
  }
}

@media (max-width: 480px) {
  .kpi__num {
    font-size: var(--fs-22);
  }

  .spec-band .spec {
    padding: 14px 16px;
  }
}
</style>
