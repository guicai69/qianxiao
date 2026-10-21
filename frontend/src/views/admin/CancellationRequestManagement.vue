<template>
  <div class="page-container">
    <header class="page-header">
      <h2>退场申请</h2>
      <p>会员在时段结束前提交的退场申请；审批通过即退款，超过 5 分钟无人处理自动通过并退款</p>
    </header>

    <section class="surface panel">
      <div class="page-toolbar">
        <el-radio-group v-model="statusFilter" @change="handleFilter">
          <el-radio-button value="">全部</el-radio-button>
          <el-radio-button value="pending">待审批</el-radio-button>
          <el-radio-button value="approved">已通过待退款</el-radio-button>
          <el-radio-button value="refunded">已退款</el-radio-button>
          <el-radio-button value="rejected">已驳回</el-radio-button>
        </el-radio-group>
      </div>

      <el-table :data="list" v-loading="loading">
        <el-table-column prop="id" label="ID" width="60">
          <template #default="{ row }"><span class="mono dim">{{ row.id }}</span></template>
        </el-table-column>
        <el-table-column label="用户" min-width="130">
          <template #default="{ row }">{{ row.user_nickname || row.user_phone }}</template>
        </el-table-column>
        <el-table-column label="订单" min-width="220">
          <template #default="{ row }">
            <span>{{ row.venue_name }} · {{ row.court_name }}</span>
            <span class="dim mono"> {{ row.booking_date }} {{ row.time_slot_display }}</span>
          </template>
        </el-table-column>
        <el-table-column label="应退金额" width="100">
          <template #default="{ row }"><span class="mono accent">¥{{ row.refund_amount }}</span></template>
        </el-table-column>
        <el-table-column prop="reason" label="原因" min-width="130" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" size="small" round effect="light">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="申请时间" width="170">
          <template #default="{ row }"><span class="mono dim">{{ formatTime(row.created_at) }}</span></template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button size="small" type="success" @click="approve(row)">通过</el-button>
              <el-button size="small" type="danger" plain @click="reject(row)">驳回</el-button>
            </template>
            <span v-else class="dim">已处理</span>
          </template>
        </el-table-column>
        <template #empty>
          <div class="empty-state"><strong>暂无退场申请</strong></div>
        </template>
      </el-table>

      <div class="table-footer">
        <el-pagination
          v-model:current-page="query.page"
          :total="total"
          :page-size="query.page_size"
          layout="total, prev, pager, next"
          @current-change="fetchData"
        />
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { cancellationApi } from '@/api/cancellations'

const list = ref([])
const total = ref(0)
const loading = ref(false)
const statusFilter = ref('')
const query = reactive({ page: 1, page_size: 20 })

const statusLabel = (s) => ({ pending: '待审批', approved: '已通过待退款', rejected: '已驳回', refunded: '已退款' }[s] || s)
const statusTag = (s) => ({ pending: 'warning', approved: 'primary', rejected: 'danger', refunded: 'success' }[s] || 'info')
const formatTime = (t) => (t || '').slice(0, 19).replace('T', ' ')

function handleFilter() { query.page = 1; fetchData() }

async function fetchData() {
  loading.value = true
  try {
    const params = { page: query.page, page_size: query.page_size }
    if (statusFilter.value) params.status = statusFilter.value
    const res = await cancellationApi.list(params)
    list.value = res.results || []
    total.value = res.count || 0
  } catch {
    // 拦截器已提示
  } finally {
    loading.value = false
  }
}

async function approve(row) {
  try {
    await ElMessageBox.confirm(
      `确认通过该退场申请？通过后立即退款 ¥${row.refund_amount} 到会员余额。`,
      '审批确认',
      { type: 'warning' },
    )
    const res = await cancellationApi.approve(row.id)
    ElMessage.success(res?.message || '已通过，已退款')
    fetchData()
  } catch {
    // canceled or handled
  }
}

async function reject(row) {
  try {
    const { value } = await ElMessageBox.prompt('驳回原因（可选）', '驳回退场申请', {
      inputPlaceholder: '如：时间太紧，无法退场',
      inputValue: '',
    })
    await cancellationApi.reject(row.id, { reject_reason: value || '' })
    ElMessage.success('已驳回')
    fetchData()
  } catch {
    // canceled or handled
  }
}

onMounted(fetchData)
</script>

<style scoped>
.panel {
  padding: 20px;
}

.panel :deep(.el-table__empty-block) {
  width: 100% !important;
}

.table-footer :deep(.el-pagination) {
  flex-wrap: wrap;
  row-gap: 8px;
}

@media (max-width: 768px) {
  .panel {
    padding: 14px;
  }
}
</style>
