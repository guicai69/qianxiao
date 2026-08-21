<template>
  <div class="dashboard-page">
    <div class="page-header">
      <h2>数据看板</h2>
      <p>场馆、场地与今日经营概况</p>
    </div>

    <el-row :gutter="16" class="summary-grid">
      <el-col
        v-for="card in summaryCards"
        :key="card.label"
        :xs="12"
        :sm="12"
        :md="8"
        :lg="6"
      >
        <el-card shadow="never" class="summary-card">
          <div class="summary-card-inner">
            <span class="summary-icon" :style="{ background: card.soft, color: card.color }">
              <el-icon :size="24"><component :is="card.icon" /></el-icon>
            </span>
            <div class="summary-meta">
              <span>{{ card.label }}</span>
              <strong>{{ card.value }}</strong>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="chart-row">
      <el-col :xs="24" :lg="14">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header-title">
              <span>各场馆场地数</span>
              <el-tag effect="plain" type="primary" round>按场馆</el-tag>
            </div>
          </template>
          <div ref="barChartRef" class="chart-box"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="10">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header-title">
              <span>场馆状态分布</span>
              <el-tag effect="plain" type="info" round>当前</el-tag>
            </div>
          </template>
          <div ref="pieChartRef" class="chart-box"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="chart-row">
      <el-col :xs="24" :lg="14">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header-title">
              <span>近 7 日营收趋势</span>
              <el-tag effect="plain" type="success" round>已支付订单</el-tag>
            </div>
          </template>
          <div ref="lineChartRef" class="chart-box"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="10">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header-title">
              <span>热门时段 Top</span>
              <el-tag effect="plain" type="warning" round>预约量</el-tag>
            </div>
          </template>
          <div ref="slotsChartRef" class="chart-box"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" class="table-card">
      <template #header>
        <div class="card-header-title">
          <span>场馆列表</span>
          <el-button link type="primary" @click="$router.push('/admin/venues')">查看全部</el-button>
        </div>
      </template>
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
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from "vue"
import * as echarts from "echarts"
import { venueApi } from "@/api/venues"
import api from "@/api"
import { statsApi } from "@/api/stats"
import {
  OfficeBuilding,
  Grid,
  UserFilled,
  Calendar,
  Money,
  TrendCharts,
} from "@element-plus/icons-vue"

const barChartRef = ref(null)
const pieChartRef = ref(null)
const lineChartRef = ref(null)
const slotsChartRef = ref(null)
const venues = ref([])
const loading = ref(true)
const totalCourts = ref(0)
const statsData = ref(null)
const trendData = ref([])
const slotsData = ref([])
let barChart = null
let pieChart = null
let lineChart = null
let slotsChart = null

const summaryCards = computed(() => [
  {
    label: "场馆总数",
    value: statsData.value?.total_venues || venues.value.length || 0,
    color: "#1976d2",
    soft: "#e8f1fb",
    icon: OfficeBuilding,
  },
  {
    label: "场地总数",
    value: statsData.value?.total_courts || totalCourts.value || 0,
    color: "#16a34a",
    soft: "#ecfdf5",
    icon: Grid,
  },
  {
    label: "会员总数",
    value: statsData.value?.total_members || 0,
    color: "#7c3aed",
    soft: "#f5f3ff",
    icon: UserFilled,
  },
  {
    label: "今日预约",
    value: statsData.value?.today_bookings || 0,
    color: "#d97706",
    soft: "#fffbeb",
    icon: Calendar,
  },
  {
    label: "今日营收",
    value: "¥" + (Number(statsData.value?.today_revenue || 0)).toFixed(2),
    color: "#059669",
    soft: "#ecfdf5",
    icon: Money,
  },
  {
    label: "累计营收",
    value: "¥" + (Number(statsData.value?.total_revenue || 0)).toFixed(2),
    color: "#0ea5e9",
    soft: "#f0f9ff",
    icon: TrendCharts,
  },
])

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
    nextTick(initCharts)
  }
}

const tooltipStyle = {
  backgroundColor: "#ffffff",
  borderColor: "#e5e7eb",
  textStyle: { color: "#1f2937" },
}

function initCharts() {
  if (!barChartRef.value || !pieChartRef.value || venues.value.length === 0) return

  barChart = echarts.init(barChartRef.value)
  barChart.setOption({
    tooltip: { trigger: "axis", ...tooltipStyle },
    grid: { left: 44, right: 20, top: 24, bottom: 36 },
    xAxis: {
      type: "category",
      data: venues.value.map((v) => v.name.substring(0, 6) + (v.name.length > 6 ? "…" : "")),
      axisLabel: { rotate: 24, fontSize: 11, color: "#64748b" },
      axisLine: { lineStyle: { color: "#e5e7eb" } },
      axisTick: { show: false },
    },
    yAxis: {
      type: "value",
      minInterval: 1,
      axisLabel: { color: "#64748b" },
      splitLine: { lineStyle: { color: "#eef1f5" } },
    },
    series: [
      {
        type: "bar",
        data: venues.value.map((v) => v.court_count || 0),
        barWidth: 22,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "#1976d2" },
            { offset: 1, color: "#93c5fd" },
          ]),
          borderRadius: [6, 6, 0, 0],
        },
      },
    ],
  })

  const active = venues.value.filter((v) => v.is_active).length
  const inactive = venues.value.length - active
  pieChart = echarts.init(pieChartRef.value)
  pieChart.setOption({
    tooltip: {
      trigger: "item",
      formatter: "{b}: {c} ({d}%)",
      ...tooltipStyle,
    },
    legend: { bottom: 0, textStyle: { color: "#64748b" } },
    series: [
      {
        type: "pie",
        radius: ["44%", "70%"],
        center: ["50%", "44%"],
        itemStyle: { borderRadius: 8, borderColor: "#ffffff", borderWidth: 4 },
        data: [
          { value: active, name: "已启用", itemStyle: { color: "#16a34a" } },
          { value: inactive, name: "已停用", itemStyle: { color: "#dc2626" } },
        ],
        label: { show: true, formatter: "{b}\n{d}%", fontSize: 13, color: "#475569" },
        emphasis: {
          scaleSize: 8,
          itemStyle: { shadowBlur: 12, shadowColor: "rgba(16,24,40,0.12)" },
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
    tooltip: {
      trigger: "axis",
      ...tooltipStyle,
      formatter: (params) => {
        const idx = params?.[0]?.dataIndex ?? 0
        const rev = revenues[idx] ?? 0
        const bk = bookings[idx] ?? 0
        return `${dates[idx]}<br/>营收：¥${rev.toFixed(2)}<br/>订单：${bk} 笔`
      },
    },
    legend: {
      top: 0,
      right: 0,
      data: ["营收", "订单数"],
      textStyle: { color: "#64748b" },
    },
    grid: { left: 52, right: 40, top: 40, bottom: 28 },
    xAxis: {
      type: "category",
      boundaryGap: false,
      data: dates,
      axisLabel: { fontSize: 11, color: "#64748b" },
      axisLine: { lineStyle: { color: "#e5e7eb" } },
      axisTick: { show: false },
    },
    yAxis: [
      {
        type: "value",
        name: "营收(¥)",
        nameTextStyle: { color: "#64748b", fontSize: 11 },
        axisLabel: { color: "#64748b" },
        splitLine: { lineStyle: { color: "#eef1f5" } },
      },
      {
        type: "value",
        name: "订单(笔)",
        nameTextStyle: { color: "#64748b", fontSize: 11 },
        minInterval: 1,
        axisLabel: { color: "#64748b" },
        splitLine: { show: false },
      },
    ],
    series: [
      {
        name: "营收",
        type: "line",
        smooth: true,
        data: revenues,
        symbol: "circle",
        symbolSize: 7,
        lineStyle: { width: 3, color: "#1976d2" },
        itemStyle: { color: "#1976d2", borderColor: "#ffffff", borderWidth: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "rgba(25, 118, 210, 0.22)" },
            { offset: 1, color: "rgba(25, 118, 210, 0.02)" },
          ]),
        },
      },
      {
        name: "订单数",
        type: "bar",
        yAxisIndex: 1,
        data: bookings,
        barWidth: 10,
        itemStyle: { color: "#93c5fd", borderRadius: [4, 4, 0, 0] },
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
    tooltip: { trigger: "axis", ...tooltipStyle },
    grid: { left: 84, right: 24, top: 16, bottom: 28 },
    xAxis: {
      type: "value",
      minInterval: 1,
      axisLabel: { color: "#64748b" },
      splitLine: { lineStyle: { color: "#eef1f5" } },
    },
    yAxis: {
      type: "category",
      data: labels,
      axisLabel: { color: "#475569", fontSize: 12 },
      axisLine: { show: false },
      axisTick: { show: false },
    },
    series: [
      {
        type: "bar",
        data: counts,
        barWidth: 14,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: "#f59e0b" },
            { offset: 1, color: "#fcd34d" },
          ]),
          borderRadius: [0, 6, 6, 0],
        },
        label: {
          show: true,
          position: "right",
          color: "#d97706",
          fontWeight: 700,
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
  gap: 16px;
}

.summary-grid {
  row-gap: 16px;
}

.summary-card {
  height: 100%;
}

.summary-card :deep(.el-card__body) {
  padding: 18px;
}

.summary-card-inner {
  display: flex;
  align-items: center;
  gap: 14px;
}

.summary-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 14px;
  flex: 0 0 48px;
}

.summary-meta {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.summary-meta span {
  color: var(--mui-muted);
  font-size: 13px;
  font-weight: 600;
}

.summary-meta strong {
  margin-top: 4px;
  color: var(--mui-text);
  font-size: 24px;
  font-weight: 800;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chart-row {
  row-gap: 16px;
}

.chart-card,
.table-card {
  width: 100%;
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

.chart-box {
  height: 320px;
}

@media (max-width: 768px) {
  .chart-box {
    height: 260px;
  }
}
</style>
