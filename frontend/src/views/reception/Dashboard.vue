<template>
  <div class="reception-dashboard">
    <div class="page-header">
      <div>
        <h2>操作台</h2>
        <p>今日预约、待处理与营收概览</p>
      </div>
      <div class="refresh-hint">
        <el-icon :class="{ spinning: refreshing }"><Refresh /></el-icon>
        <span>{{ lastUpdated ? "更新于 " + lastUpdated : "加载中…" }}</span>
      </div>
    </div>

    <el-row :gutter="16" class="stat-grid">
      <el-col :xs="24" :sm="8">
        <el-card shadow="never" class="stat-card">
          <div class="stat-card-inner">
            <span class="stat-icon soft-blue"><el-icon :size="24"><Calendar /></el-icon></span>
            <div>
              <span>今日预约</span>
              <strong>{{ stats.today_bookings }}</strong>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-card shadow="never" class="stat-card">
          <div class="stat-card-inner">
            <span class="stat-icon soft-amber"><el-icon :size="24"><Warning /></el-icon></span>
            <div>
              <span>待处理</span>
              <strong>{{ stats.today_pending }}</strong>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-card shadow="never" class="stat-card">
          <div class="stat-card-inner">
            <span class="stat-icon soft-green"><el-icon :size="24"><Money /></el-icon></span>
            <div>
              <span>今日营收</span>
              <strong>¥{{ Number(stats.today_revenue || 0).toFixed(2) }}</strong>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="content-row">
      <el-col :xs="24" :lg="14">
        <el-card shadow="never" class="table-card">
          <template #header>
            <div class="card-header-title">
              <span>今日预约</span>
              <div class="header-actions">
                <el-tag effect="plain" type="warning" round>{{ pendingCount }} 笔待处理</el-tag>
                <el-button link type="primary" @click="$router.push('/admin/bookings')">全部订单</el-button>
              </div>
            </div>
          </template>
          <el-table :data="todayBookings" v-loading="loading" empty-text="今日暂无预约">
            <el-table-column label="用户" min-width="110">
              <template #default="{ row }">{{ row.user_nickname || row.user_phone }}</template>
            </el-table-column>
            <el-table-column prop="court_name" label="场地" width="90" />
            <el-table-column prop="time_slot_display" label="时段" width="110" />
            <el-table-column label="金额" width="90">
              <template #default="{ row }">
                <span class="amount">¥{{ row.amount }}</span>
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
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="10">
        <div class="side-stack">
          <el-card shadow="never" class="chart-card">
            <template #header>
              <div class="card-header-title">
                <span>近 7 日营收</span>
                <el-tag effect="plain" type="success" round>趋势</el-tag>
              </div>
            </template>
            <div ref="trendChartRef" class="chart-box"></div>
          </el-card>

          <el-card shadow="never" class="quick-card">
            <template #header>
              <span class="quick-title">快捷入口</span>
            </template>
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
          </el-card>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from "vue"
import * as echarts from "echarts"
import { ElMessage, ElMessageBox } from "element-plus"
import { useIntervalFn, useDocumentVisibility } from "@vueuse/core"
import {
  Calendar,
  Warning,
  Money,
  OfficeBuilding,
  Tickets,
  Wallet,
  Refresh,
} from "@element-plus/icons-vue"
import { statsApi } from "@/api/stats"
import { bookingApi } from "@/api/bookings"
import { paymentApi } from "@/api/payments"

const stats = ref({ today_bookings: 0, today_pending: 0, today_revenue: 0 })
const todayBookings = ref([])
const trendData = ref([])
const loading = ref(false)
const refreshing = ref(false)
const lastUpdated = ref("")
const trendChartRef = ref(null)
let trendChart = null

const pendingCount = computed(() =>
  todayBookings.value.filter((b) => b.status === "pending").length
)

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
  refreshing.value = true
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
    refreshing.value = false
  }
}

function initChart() {
  if (!trendChartRef.value) return
  if (!trendChart) trendChart = echarts.init(trendChartRef.value)
  const dates = trendData.value.map((d) => String(d.date).slice(5))
  const revenues = trendData.value.map((d) => Number(d.revenue || 0))
  trendChart.setOption({
    tooltip: {
      trigger: "axis",
      backgroundColor: "#ffffff",
      borderColor: "#e5e7eb",
      textStyle: { color: "#1f2937" },
      formatter: (params) => {
        const idx = params?.[0]?.dataIndex ?? 0
        return `${dates[idx]}<br/>营收：¥${(revenues[idx] ?? 0).toFixed(2)}`
      },
    },
    grid: { left: 52, right: 20, top: 24, bottom: 28 },
    xAxis: {
      type: "category",
      boundaryGap: false,
      data: dates,
      axisLabel: { fontSize: 11, color: "#64748b" },
      axisLine: { lineStyle: { color: "#e5e7eb" } },
      axisTick: { show: false },
    },
    yAxis: {
      type: "value",
      axisLabel: { color: "#64748b" },
      splitLine: { lineStyle: { color: "#eef1f5" } },
    },
    series: [
      {
        type: "line",
        smooth: true,
        data: revenues,
        symbol: "circle",
        symbolSize: 7,
        lineStyle: { width: 3, color: "#16a34a" },
        itemStyle: { color: "#16a34a", borderColor: "#ffffff", borderWidth: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "rgba(22, 163, 74, 0.22)" },
            { offset: 1, color: "rgba(22, 163, 74, 0.02)" },
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
  window.addEventListener("resize", handleResize)
})

onUnmounted(() => {
  pauseTimer()
  trendChart?.dispose()
  window.removeEventListener("resize", handleResize)
})
</script>

<style scoped>
.reception-dashboard {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
}

.refresh-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--mui-muted);
  font-size: 13px;
  font-weight: 600;
}

.refresh-hint .el-icon {
  color: var(--mui-primary);
}

.spinning {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.stat-grid,
.content-row {
  row-gap: 16px;
}

.stat-card {
  height: 100%;
}

.stat-card :deep(.el-card__body) {
  padding: 18px;
}

.stat-card-inner {
  display: flex;
  align-items: center;
  gap: 14px;
}

.stat-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 14px;
}

.soft-blue {
  color: #1976d2;
  background: #e8f1fb;
}

.soft-amber {
  color: #d97706;
  background: #fffbeb;
}

.soft-green {
  color: #16a34a;
  background: #ecfdf5;
}

.stat-card-inner div {
  display: flex;
  flex-direction: column;
}

.stat-card-inner div span {
  color: var(--mui-muted);
  font-size: 13px;
  font-weight: 600;
}

.stat-card-inner div strong {
  margin-top: 4px;
  color: var(--mui-text);
  font-size: 26px;
  font-weight: 800;
}

.table-card,
.chart-card,
.quick-card {
  width: 100%;
}

.side-stack {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-header-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.card-header-title span {
  font-size: 15px;
  font-weight: 700;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.amount {
  color: var(--mui-primary);
  font-weight: 800;
}

.chart-box {
  height: 260px;
}

.quick-title {
  font-weight: 700;
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

@media (max-width: 640px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
