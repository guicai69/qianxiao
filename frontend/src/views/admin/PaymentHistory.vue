<template>
  <div class="page-container">
    <header class="page-header">
      <h2>支付记录</h2>
      <p>查看充值、消费与退款记录及对应用户账号</p>
    </header>

    <section class="surface panel">
      <div class="page-toolbar">
        <el-tabs v-model="activeType" @tab-change="fetchData" class="toolbar-tabs">
          <el-tab-pane label="全部" name="" />
          <el-tab-pane label="充值记录" name="recharge" />
          <el-tab-pane label="消费记录" name="booking" />
          <el-tab-pane label="退款记录" name="refund" />
        </el-tabs>

        <div class="toolbar-actions">
          <el-button @click="handleExport">
            <el-icon class="el-icon--left"><Download /></el-icon>导出CSV
          </el-button>
        </div>
      </div>

      <el-table :data="list" v-loading="loading">
        <el-table-column label="用户账号" min-width="180">
          <template #default="{ row }">
            <div class="user-cell">
              <span class="user-avatar">
                {{ (row.user_nickname || row.user_phone || "U").slice(0, 1) }}
              </span>
              <div class="user-copy">
                <strong>{{ row.user_nickname || "未设置昵称" }}</strong>
                <span class="mono">{{ row.user_phone }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="typeTag(row.type)" effect="light" round size="small">
              {{ typeLabel(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="金额" width="150" align="right">
          <template #default="{ row }">
            <div class="amount-cell">
              <span class="amount mono">¥{{ row.amount }}</span>
              <span v-if="row.bonus && Number(row.bonus) > 0" class="bonus-text">
                +送 ¥{{ row.bonus }}
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="方式" width="110">
          <template #default="{ row }">
            {{ methodLabel(row.method) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag
              :type="row.status === 'success' ? 'success' : 'danger'"
              effect="light"
              round
              size="small"
            >
              {{ row.status === "success" ? "成功" : "失败" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="关联订单" min-width="200">
          <template #default="{ row }">
            <div v-if="row.booking" class="booking-cell">
              <strong class="mono">#{{ row.booking }}</strong>
              <span v-if="row.booking_court">
                {{ row.booking_court }} · {{ row.booking_date || "" }} {{ row.booking_time || "" }}
              </span>
            </div>
            <span v-else class="dim">—</span>
          </template>
        </el-table-column>
        <el-table-column label="时间" min-width="180">
          <template #default="{ row }">
            <span class="mono dim">{{ row.created_at?.slice(0, 19).replace("T", " ") }}</span>
          </template>
        </el-table-column>

        <template #empty>
          <div class="empty-state">
            <strong>还没有支付记录</strong>
            <span>用户充值或下单支付后，流水会按时间倒序出现在这里。</span>
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
import { ElMessage } from "element-plus"
import { Download } from "@element-plus/icons-vue"
import { paymentApi } from "@/api/payments"
import { downloadBlob } from "@/utils/download"

const list = ref([])
const total = ref(0)
const loading = ref(false)
const activeType = ref("")
const query = reactive({ page: 1, page_size: 20 })

const typeTag = (type) =>
  ({ recharge: "success", booking: "primary", refund: "warning" }[type] || "info")
const typeLabel = (type) =>
  ({ recharge: "充值", booking: "消费", refund: "退款" }[type] || type)
const methodLabel = (method) =>
  ({ balance: "余额", wechat: "微信", alipay: "支付宝" }[method] || method)

async function fetchData() {
  loading.value = true
  try {
    const params = { ...query }
    if (activeType.value) params.type = activeType.value
    const res = await paymentApi.list(params)
    list.value = res.results || []
    total.value = res.count || 0
  } catch {
    ElMessage.error("获取支付记录失败")
  } finally {
    loading.value = false
  }
}

async function handleExport() {
  try {
    const params = {}
    if (activeType.value) params.type = activeType.value
    const blob = await paymentApi.exportCsv(params)
    downloadBlob(blob, "支付记录.csv")
    ElMessage.success("导出成功")
  } catch {
    ElMessage.error("导出失败")
  }
}

onMounted(fetchData)
</script>

<style scoped>
.panel {
  padding: 20px;
}

.panel :deep(.page-toolbar) {
  padding-bottom: 6px;
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

.toolbar-tabs {
  flex: 1 1 auto;
  min-width: 0;
}

.toolbar-tabs :deep(.el-tabs__header) {
  margin-bottom: 0;
}

.toolbar-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.amount-cell {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.amount {
  color: var(--ink-1);
  font-weight: 700;
}

.bonus-text {
  color: var(--up);
  font-size: var(--fs-12);
  font-weight: 700;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 10px;
  color: var(--on-accent);
  background: var(--accent);
  font-size: var(--fs-13);
  font-weight: 800;
  flex: 0 0 34px;
}

.user-copy {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.user-copy strong {
  color: var(--ink-1);
  font-size: var(--fs-13);
  font-weight: 700;
}

.user-copy span {
  color: var(--ink-3);
  font-size: var(--fs-12);
}

.booking-cell {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.booking-cell strong {
  color: var(--ink-1);
  font-size: var(--fs-13);
  font-weight: 700;
}

.booking-cell span {
  margin-top: 2px;
  color: var(--ink-3);
  font-size: var(--fs-12);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.table-footer :deep(.el-pagination) {
  flex-wrap: wrap;
  row-gap: 8px;
}

@media (max-width: 768px) {
  .panel {
    padding: 14px;
  }

  .toolbar-actions {
    width: 100%;
  }

  .toolbar-actions :deep(.el-button) {
    flex: 1 1 auto;
  }
}
</style>
