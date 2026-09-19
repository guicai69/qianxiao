<template>
  <div class="reception-dashboard">
    <div class="page-header">
      <div>
        <h2>今日值班</h2>
        <p>今日到店与待签到订单，收款即核销</p>
      </div>
      <span class="stamp mono">{{ lastUpdated ? `更新于 ${lastUpdated}` : "同步中" }}</span>
    </div>

    <!-- 今日概览：发丝线规格带，不是一排卡片 -->
    <section class="spec-band">
      <div v-for="(item, i) in overview" :key="item.label" class="spec">
        <div
          class="spec__num"
          :class="{ 'count-up': ready }"
          :style="{ '--i': String(i) }"
        >
          {{ item.value }}
        </div>
        <div class="spec__label">{{ item.label }}</div>
      </div>
    </section>

    <!-- 主体：今日到店 / 待签到，每行可直接收款核销 -->
    <article class="panel">
      <header class="panel__head">
        <h3>今日到店 / 待签到</h3>
        <div class="head-actions">
          <el-tag effect="plain" type="warning" round>{{ pendingCount }} 笔待处理</el-tag>
          <el-button link type="primary" @click="$router.push('/admin/bookings')">
            全部订单
          </el-button>
        </div>
      </header>
      <!-- 窄屏：表格会横向滚动且固定操作列压住数据，改成一行一位的名单 -->
      <ul v-if="isNarrow" v-loading="booting" class="roster">
        <li v-for="row in todayBookings" :key="row.id" class="roster__row">
          <div class="roster__who">
            <strong>{{ row.user_nickname || row.user_phone }}</strong>
            <span class="roster__meta mono">
              {{ row.court_name }} · {{ row.time_slot_display }} · ¥{{ row.amount }}
            </span>
          </div>
          <div class="roster__act">
            <el-tag
              :type="{ pending: 'warning', paid: 'success', cancelled: 'info' }[row.status]"
              effect="light"
              round
              size="small"
            >
              {{ { pending: "待支付", paid: "已支付", cancelled: "已取消" }[row.status] }}
            </el-tag>
            <el-button
              v-if="row.status === 'pending'"
              type="success"
              @click="handlePay(row)"
            >
              收款
            </el-button>
            <el-button v-if="row.status !== 'cancelled'" @click="handleCancel(row)">
              取消
            </el-button>
          </div>
        </li>
        <li v-if="!booting && !todayBookings.length" class="roster__empty">今日暂无预约</li>
      </ul>

      <el-table v-else :data="todayBookings" v-loading="booting" empty-text="今日暂无预约">
        <el-table-column label="用户" min-width="110">
          <template #default="{ row }">{{ row.user_nickname || row.user_phone }}</template>
        </el-table-column>
        <el-table-column prop="court_name" label="场地" width="90" />
        <el-table-column prop="time_slot_display" label="时段" width="110" />
        <el-table-column label="金额" width="90">
          <template #default="{ row }">
            <span class="amount mono">¥{{ row.amount }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag
              :type="{ pending: 'warning', paid: 'success', cancelled: 'info' }[row.status]"
              effect="light"
              round
              size="small"
            >
              {{ { pending: "待支付", paid: "已支付", cancelled: "已取消" }[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending'"
              size="small"
              type="success"
              @click="handlePay(row)"
            >
              收款
            </el-button>
            <el-button
              v-if="row.status !== 'cancelled'"
              size="small"
              @click="handleCancel(row)"
            >
              取消
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </article>

    <section class="lower">
      <article class="panel">
        <header class="panel__head">
          <h3>近 7 日营收</h3>
          <span class="caps">已支付订单</span>
        </header>
        <div class="chart-shell">
          <div ref="trendChartRef" class="chart-box"></div>
          <p v-if="ready && !trendData.length" class="chart-empty">近 7 日暂无营收记录</p>
        </div>
      </article>

      <article class="panel">
        <header class="panel__head">
          <h3>快捷入口</h3>
        </header>
        <div class="quick-actions">
          <el-button type="primary" @click="$router.push('/admin/venues')">
            <el-icon><OfficeBuilding /></el-icon>场馆管理
          </el-button>
          <el-button @click="$router.push('/admin/bookings')">
            <el-icon><Tickets /></el-icon>预约管理
          </el-button>
          <el-button @click="$router.push('/admin/payments')">
            <el-icon><Wallet /></el-icon>支付记录
          </el-button>
        </div>
      </article>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from "vue"
import * as echarts from "echarts"
import { ElMessage, ElMessageBox } from "element-plus"
import { useIntervalFn, useDocumentVisibility } from "@vueuse/core"
import { OfficeBuilding, Tickets, Wallet } from "@element-plus/icons-vue"
import { statsApi } from "@/api/stats"
import { bookingApi } from "@/api/bookings"
import { paymentApi } from "@/api/payments"
import { CHART_COLORS, CHART_ANIMATION, alpha, chartAxis, chartTooltip } from "@/utils/chartTheme"

const stats = ref({ today_bookings: 0, today_pending: 0, today_revenue: 0 })
const todayBookings = ref([])
const trendData = ref([])
const booting = ref(true)
const ready = ref(false)
const lastUpdated = ref("")
const trendChartRef = ref(null)
let trendChart = null

/* 窄屏换名单式列表：横向滚动的表格在手机上会把固定操作列压在数据上 */
const narrowQuery =
  typeof window !== "undefined" ? matchMedia("(max-width: 780px)") : null
const isNarrow = ref(!!narrowQuery?.matches)

function onNarrowChange(e) {
  isNarrow.value = e.matches
}

const pendingCount = computed(() =>
  todayBookings.value.filter((b) => b.status === "pending").length
)

/* 顶部一行概览，全部是统计接口已有字段 */
const overview = computed(() => {
  const s = stats.value || {}
  return [
    { label: "今日预约", value: String(s.today_bookings || 0) },
    { label: "待处理", value: String(s.today_pending || 0) },
    { label: "今日营收", value: `¥${Number(s.today_revenue || 0).toFixed(2)}` },
    { label: "已收款", value: String(s.today_paid || 0) },
  ]
})

function todayStr() {
  const d = new Date()
  const m = String(d.getMonth() + 1).padStart(2, "0")
  const day = String(d.getDate()).padStart(2, "0")
  return `${d.getFullYear()}-${m}-${day}`
}

function fmtTime() {
  const d = new Date()
  return d.toLocaleTimeString("zh-CN", { hour12: false })
}

async function refresh() {
  try {
    const [stRes, bookingRes, trendRes] = await Promise.all([
      statsApi.overview(),
      bookingApi.list({ date: todayStr(), page_size: 20 }),
      statsApi.revenueTrend(7),
    ])
    stats.value = stRes
    todayBookings.value = bookingRes.results || []
    trendData.value = trendRes?.days || []
    lastUpdated.value = fmtTime()
    nextTick(initChart)
  } catch {
    // handled by request interceptor
  } finally {
    /* 只在首屏给一次加载态，之后每 5 秒刷新不再重挂骨架 */
    booting.value = false
    ready.value = true
  }
}

function initChart() {
  if (!trendChartRef.value) return
  if (!trendChart) trendChart = echarts.init(trendChartRef.value)
  const dates = trendData.value.map((d) => String(d.date).slice(5))
  const revenues = trendData.value.map((d) => Number(d.revenue || 0))
  trendChart.setOption({
    animation: CHART_ANIMATION,
    tooltip: chartTooltip({
      trigger: "axis",
      formatter: (params) => {
        const idx = params?.[0]?.dataIndex ?? 0
        return `${dates[idx]}<br/>营收：¥${(revenues[idx] ?? 0).toFixed(2)}`
      },
    }),
    grid: { left: 4, right: 28, top: 16, bottom: 4, containLabel: true },
    xAxis: chartAxis({
      type: "category",
      boundaryGap: false,
      data: dates,
      splitLine: { show: false },
    }),
    yAxis: chartAxis({ type: "value" }),
    series: [
      {
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
    ],
  })
}

async function handlePay(row) {
  try {
    await ElMessageBox.confirm("确认收到该订单的款项？", "收款确认", { type: "info" })
    await paymentApi.confirmCash({ booking_id: row.id })
    ElMessage.success("已支付")
    refresh()
  } catch {
    // cancelled or handled
  }
}

async function handleCancel(row) {
  try {
    await ElMessageBox.confirm("确定取消该预约？", "取消确认", { type: "warning" })
    const res = await bookingApi.cancel(row.id)
    const refund = res?.data?.refund_amount
    ElMessage.success(refund ? `已取消，退款 ¥${refund}` : "已取消")
    refresh()
  } catch {
    // cancelled or handled
  }
}

// 每 5 秒自动刷新；页面重新可见时立即同步
const visibility = useDocumentVisibility()
watch(visibility, (v) => {
  if (v === "visible") refresh()
})

const { pause: pauseTimer } = useIntervalFn(refresh, 5000)

function handleResize() {
  trendChart?.resize()
}

onMounted(() => {
  refresh()
  narrowQuery?.addEventListener("change", onNarrowChange)
  window.addEventListener("resize", handleResize)
})

onUnmounted(() => {
  pauseTimer()
  narrowQuery?.removeEventListener("change", onNarrowChange)
  trendChart?.dispose()
  window.removeEventListener("resize", handleResize)
})
</script>

<style scoped>
.reception-dashboard {
  display: flex;
  flex-direction: column;
  gap: 18px;
  min-width: 0;
}

.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.stamp {
  color: var(--ink-4);
  font-size: var(--fs-12);
  letter-spacing: 0.04em;
  white-space: nowrap;
}

/* ---------- 今日概览 ---------- */

.spec-band .spec {
  padding: 18px 20px;
}

.spec-band .spec__num {
  font-size: var(--fs-22);
}

/* ---------- 面板 ---------- */

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

.head-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.amount {
  color: var(--accent);
  font-weight: 700;
}

/* ---------- 窄屏名单：一行一位，操作直接给到手上 ---------- */

.roster {
  list-style: none;
  margin: 0;
  padding: 0;
}

.roster__row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px 16px;
  flex-wrap: wrap;
  padding: 14px 0;
  border-bottom: 1px solid var(--border-soft);
  min-width: 0;
}

.roster__row:last-child {
  border-bottom: 0;
}

.roster__who {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
  flex: 1 1 140px;
}

.roster__who strong {
  font-size: var(--fs-14);
  font-weight: 700;
  color: var(--ink-1);
  overflow-wrap: anywhere;
}

.roster__meta {
  font-size: var(--fs-12);
  color: var(--ink-3);
  overflow-wrap: anywhere;
}

.roster__act {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 0 0 auto;
}

.roster__act .el-button {
  min-height: 34px;
  margin-left: 0;
}

.roster__empty {
  padding: 40px 0;
  text-align: center;
  color: var(--ink-3);
  font-size: var(--fs-13);
}

.lower {
  display: grid;
  grid-template-columns: minmax(0, 1.55fr) minmax(0, 1fr);
  align-items: start;
  gap: 14px;
}

.chart-shell {
  position: relative;
  min-width: 0;
}

.chart-box {
  height: 260px;
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

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.quick-actions .el-button {
  min-width: 120px;
  margin-left: 0;
}

/* ---------- 断点 ---------- */

@media (max-width: 1100px) {
  .lower {
    grid-template-columns: minmax(0, 1fr);
  }
}

@media (max-width: 640px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .spec-band .spec {
    padding: 14px 16px;
  }

  .chart-box {
    height: 220px;
  }
}

@media (max-width: 400px) {
  .spec-band .spec__num {
    font-size: var(--fs-18);
  }
}
</style>
