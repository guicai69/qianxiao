<template>
  <div class="page-container">
    <header class="page-header">
      <h2>预约管理</h2>
      <p>按日期、场馆与状态筛选预约，前台可代为收款、签到与取消</p>
    </header>

    <section class="surface panel">
      <div class="page-toolbar">
        <el-form :model="query" inline class="filter-form">
          <el-form-item label="日期">
            <el-date-picker v-model="query.date" type="date" value-format="YYYY-MM-DD" clearable class="w-date" />
          </el-form-item>
          <el-form-item label="场馆">
            <el-select v-model="query.venue" clearable placeholder="全部" class="w-160">
              <el-option v-for="v in venues" :key="v.id" :label="v.name" :value="v.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="query.status" clearable placeholder="全部" class="w-120">
              <el-option label="待支付" value="pending" /><el-option label="已支付" value="paid" /><el-option label="已取消" value="cancelled" />
            </el-select>
          </el-form-item>
          <el-form-item class="filter-actions">
            <el-button type="primary" @click="fetchData">搜索</el-button>
            <el-button @click="reset">重置</el-button>
          </el-form-item>
        </el-form>

        <div class="toolbar-actions">
          <el-button @click="handleExport">
            <el-icon class="el-icon--left"><Download /></el-icon>导出CSV
          </el-button>
        </div>
      </div>

      <el-table :data="list" v-loading="loading">
        <el-table-column prop="id" label="ID" width="56">
          <template #default="{ row }"><span class="mono dim">{{ row.id }}</span></template>
        </el-table-column>
        <el-table-column label="用户" width="116" show-overflow-tooltip>
          <template #default="{ row }">{{ row.user_nickname || row.user_phone }}</template>
        </el-table-column>
        <el-table-column prop="venue_name" label="场馆" min-width="140" show-overflow-tooltip />
        <el-table-column prop="court_name" label="场地" width="80" />
        <el-table-column prop="date" label="日期" width="106">
          <template #default="{ row }"><span class="mono">{{ row.date }}</span></template>
        </el-table-column>
        <el-table-column prop="time_slot_display" label="时段" width="112">
          <template #default="{ row }"><span class="mono">{{ row.time_slot_display }}</span></template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="112" align="right">
          <template #default="{ row }">
            <div class="amount-cell">
              <span class="mono amount">¥{{ row.amount }}</span>
              <span
                v-if="row.discount_rate && Number(row.discount_rate) < 1"
                class="discount-text mono"
              >
                {{ discountText(row.discount_rate) }}
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="88">
          <template #default="{ row }">
            <el-tag :type="orderStateTag(row)" effect="light" round size="small">
              {{ orderStateLabel(row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="签到" width="88">
          <template #default="{ row }">
            <template v-if="row.status === 'paid'">
              <el-tag v-if="row.checked_in" type="success" effect="light" round size="small">已签到</el-tag>
              <el-tag v-else type="info" effect="light" round size="small">未签到</el-tag>
            </template>
            <span v-else class="dim">—</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="190" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="handlePay(row)" v-if="row.status==='pending' && !row.is_expired">收款</el-button>
            <el-button size="small" type="success" @click="handleCheckIn(row)" v-if="row.status==='paid' && !row.checked_in && !row.is_finished">签到</el-button>
            <el-button size="small" @click="handleCancel(row)" v-if="row.status!=='cancelled'">取消</el-button>
          </template>
        </el-table-column>

        <template #empty>
          <div class="empty-state">
            <strong>没有符合条件的预约</strong>
            <span>换个日期，或清空场馆与状态筛选再看一次。</span>
          </div>
        </template>
      </el-table>

      <div class="table-footer">
        <el-pagination
          v-model:current-page="query.page"
          v-model:page-size="query.page_size"
          :total="total"
          :pager-count="5"
          layout="total, prev, pager, next"
          @current-change="fetchData"
        />
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import { Download } from "@element-plus/icons-vue"
import { bookingApi } from "@/api/bookings"
import { paymentApi } from "@/api/payments"
import { venueApi } from "@/api/venues"
import { downloadBlob } from "@/utils/download"
import { discountText, orderStateLabel, orderStateTag } from "@/utils/format"

const list = ref([]); const total = ref(0); const loading = ref(false); const venues = ref([])
const query = reactive({ page: 1, page_size: 20, date: "", venue: "", status: "" })

async function fetchVenues() {
  try { const r = await venueApi.list({ page_size: 100 }); venues.value = r.results || [] } catch {}
}

async function fetchData() {
  loading.value = true
  try {
    const p = { page: query.page, page_size: query.page_size }
    if (query.date) p.date = query.date
    if (query.venue) p.venue = query.venue
    if (query.status) p.status = query.status
    const r = await bookingApi.list(p)
    list.value = r.results || []; total.value = r.count || 0
  } catch { ElMessage.error("获取预约列表失败") }
  finally { loading.value = false }
}

function reset() { query.page = 1; query.date = ""; query.venue = ""; query.status = ""; fetchData() }

async function handlePay(row) {
  try { await ElMessageBox.confirm("确认收到该订单的款项？", "收款确认", { type: "info" }); await paymentApi.confirmCash({ booking_id: row.id }); ElMessage.success("已支付"); fetchData() } catch {}
}
async function handleCancel(row) {
  try {
    await ElMessageBox.confirm("确定取消该预约？", "取消确认", { type: "warning" })
    const res = await bookingApi.cancel(row.id)
    const refund = res?.data?.refund_amount
    ElMessage.success(refund ? `已取消，退款 ¥${refund}` : "已取消")
    fetchData()
  } catch {}
}

async function handleCheckIn(row) {
  try {
    await ElMessageBox.confirm("确认该订单用户已到店？", "签到确认", { type: "info" })
    await bookingApi.checkIn(row.id)
    ElMessage.success("签到成功")
    fetchData()
  } catch {}
}

async function handleExport() {
  try {
    const params = {}
    if (query.date) params.date = query.date
    if (query.venue) params.venue = query.venue
    if (query.status) params.status = query.status
    const blob = await bookingApi.exportCsv(params)
    downloadBlob(blob, "预约订单.csv")
    ElMessage.success("导出成功")
  } catch {
    ElMessage.error("导出失败")
  }
}

onMounted(() => { fetchVenues(); fetchData() })
</script>

<style scoped>
.panel {
  padding: 20px;
}

.panel :deep(.page-toolbar) {
  padding-bottom: 14px;
  border-bottom: 1px solid var(--border-soft);
}

/* 固定列要有不透明底色，否则横向滚动时下面的单元格会透出来 */
.panel :deep(.el-table) {
  --el-table-tr-bg-color: var(--surface);
}

/* 表格空态要占满整宽，不能跟着表格布局计算塌成窄条 */
.panel :deep(.el-table__empty-block) {
  width: 100% !important;
}

.panel :deep(.el-table__empty-text) {
  width: 100%;
  line-height: normal;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  row-gap: 10px;
}

.filter-form :deep(.el-form-item) {
  margin: 0 14px 0 0;
}

.filter-form :deep(.el-form-item__label) {
  color: var(--ink-3);
  font-weight: 600;
}

.filter-form :deep(.filter-actions .el-form-item__content) {
  gap: 8px;
}

.w-160 { width: 160px; }
.w-120 { width: 120px; }
.w-date { width: 150px; }

.amount {
  color: var(--ink-1);
  font-weight: 700;
}

.amount-cell {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.discount-text {
  color: var(--accent);
  font-weight: 700;
}

.table-footer :deep(.el-pagination) {
  flex-wrap: wrap;
  row-gap: 8px;
}

@media (max-width: 768px) {
  .panel {
    padding: 14px;
  }

  .filter-form :deep(.el-form-item) {
    flex: 1 1 100%;
    margin-right: 0;
  }

  .filter-form :deep(.el-form-item__content) {
    flex: 1 1 auto;
    min-width: 0;
  }

  .filter-form :deep(.el-select),
  .filter-form :deep(.el-date-editor) {
    width: 100%;
  }

  .toolbar-actions {
    width: 100%;
  }

  .toolbar-actions :deep(.el-button) {
    flex: 1 1 auto;
  }
}
</style>
