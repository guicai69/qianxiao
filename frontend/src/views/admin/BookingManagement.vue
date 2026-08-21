<template>
  <div>
    <el-card>
      <el-form :model="query" inline>
        <el-form-item label="日期"><el-date-picker v-model="query.date" type="date" value-format="YYYY-MM-DD" clearable /></el-form-item>
        <el-form-item label="场馆">
          <el-select v-model="query.venue" clearable placeholder="全部" style="width:160px">
            <el-option v-for="v in venues" :key="v.id" :label="v.name" :value="v.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.status" clearable placeholder="全部" style="width:120px">
            <el-option label="待支付" value="pending" /><el-option label="已支付" value="paid" /><el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">搜索</el-button>
          <el-button @click="reset">重置</el-button>
          <el-button @click="handleExport">
            <el-icon class="el-icon--left"><Download /></el-icon>导出CSV
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card style="margin-top:16px">
      <el-table :data="list" border stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="用户" width="120"><template #default="{ row }">{{ row.user_nickname || row.user_phone }}</template></el-table-column>
        <el-table-column prop="venue_name" label="场馆" min-width="140" />
        <el-table-column prop="court_name" label="场地" width="80" />
        <el-table-column prop="date" label="日期" width="110" />
        <el-table-column prop="time_slot_display" label="时段" width="100" />
        <el-table-column prop="amount" label="金额" width="80" />
        <el-table-column label="折扣" width="80">
          <template #default="{ row }">
            <span
              v-if="row.discount_rate && Number(row.discount_rate) < 1"
              class="discount-text"
            >
              {{ discountText(row.discount_rate) }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }"><el-tag :type="{pending:'warning',paid:'success',cancelled:'info'}[row.status]" size="small">{{ {pending:"待支付",paid:"已支付",cancelled:"已取消"}[row.status] }}</el-tag></template>
        </el-table-column>
        <el-table-column label="签到" width="90">
          <template #default="{ row }">
            <template v-if="row.status === 'paid'">
              <el-tag v-if="row.checked_in" type="success" size="small">已签到</el-tag>
              <el-tag v-else type="info" size="small">未签到</el-tag>
            </template>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handlePay(row)" v-if="row.status==='pending'">收款</el-button>
            <el-button size="small" type="success" @click="handleCheckIn(row)" v-if="row.status==='paid' && !row.checked_in">签到</el-button>
            <el-button size="small" @click="handleCancel(row)" v-if="row.status!=='cancelled'">取消</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.page_size" :total="total" layout="total, prev, pager, next" @current-change="fetchData" style="margin-top:16px" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import { Download } from "@element-plus/icons-vue"
import { bookingApi } from "@/api/bookings"
import { venueApi } from "@/api/venues"
import { downloadBlob } from "@/utils/download"

const list = ref([]); const total = ref(0); const loading = ref(false); const venues = ref([])
const query = reactive({ page: 1, page_size: 20, date: "", venue: "", status: "" })

const discountText = (rate) => {
  const value = Number(rate)
  if (value >= 1) return "原价"
  return `${Math.round(value * 100)}折`
}

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
  try { await ElMessageBox.confirm("确认收到该订单的款项？", "收款确认", { type: "info" }); await bookingApi.pay(row.id); ElMessage.success("已支付"); fetchData() } catch {}
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
.discount-text {
  color: var(--mui-primary);
  font-weight: 700;
}
</style>
