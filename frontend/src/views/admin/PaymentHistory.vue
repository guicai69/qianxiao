<template>
  <div class="admin-payments">
    <div class="page-header header-row">
      <div>
        <h2>支付记录</h2>
        <p>查看充值、消费与退款记录及对应用户账号</p>
      </div>
      <el-button @click="handleExport">
        <el-icon class="el-icon--left"><Download /></el-icon>导出CSV
      </el-button>
    </div>

    <el-card shadow="never">
      <el-tabs v-model="activeType" @tab-change="fetchData">
        <el-tab-pane label="全部" name="" />
        <el-tab-pane label="充值记录" name="recharge" />
        <el-tab-pane label="消费记录" name="booking" />
        <el-tab-pane label="退款记录" name="refund" />
      </el-tabs>

      <el-table :data="list" v-loading="loading" empty-text="暂无记录">
        <el-table-column label="用户账号" min-width="170">
          <template #default="{ row }">
            <div class="user-cell">
              <span class="user-avatar">
                {{ (row.user_nickname || row.user_phone || "U").slice(0, 1) }}
              </span>
              <div class="user-copy">
                <strong>{{ row.user_nickname || "未设置昵称" }}</strong>
                <span>{{ row.user_phone }}</span>
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
        <el-table-column label="金额" width="150">
          <template #default="{ row }">
            <span class="amount">¥{{ row.amount }}</span>
            <span v-if="row.bonus && Number(row.bonus) > 0" class="bonus-text">
              +送 ¥{{ row.bonus }}
            </span>
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
              :type="row.status === 'success' ? 'success' : 'info'"
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
              <strong>#{{ row.booking }}</strong>
              <span v-if="row.booking_court">
                {{ row.booking_court }} · {{ row.booking_date || "" }} {{ row.booking_time || "" }}
              </span>
            </div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="时间" min-width="170">
          <template #default="{ row }">
            {{ row.created_at?.slice(0, 19).replace("T", " ") }}
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="fetchData"
        class="table-footer"
      />
    </el-card>
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
  ({ recharge: "success", booking: "warning", refund: "info" }[type] || "info")
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
.admin-payments {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.bonus-text {
  margin-left: 6px;
  color: var(--mui-success);
  font-size: 12px;
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
  color: #ffffff;
  background: var(--mui-primary);
  font-size: 13px;
  font-weight: 800;
  flex: 0 0 34px;
}

.user-copy {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.user-copy strong {
  color: var(--mui-text);
  font-size: 13px;
  font-weight: 800;
}

.user-copy span {
  color: var(--mui-muted);
  font-size: 12px;
}

.amount {
  color: var(--mui-primary);
  font-weight: 800;
}

.booking-cell {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.booking-cell strong {
  color: var(--mui-text);
  font-size: 13px;
  font-weight: 800;
}

.booking-cell span {
  margin-top: 2px;
  color: var(--mui-muted);
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
