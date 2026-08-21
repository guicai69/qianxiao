<template>
  <div class="payment-history">
    <div class="page-header">
      <h2>支付记录</h2>
      <p>查看充值记录、消费记录与当前余额</p>
    </div>

    <div class="history-layout">
      <el-card shadow="never" class="balance-card">
        <span class="balance-icon"><el-icon :size="24"><Wallet /></el-icon></span>
        <span class="balance-label">当前余额</span>
        <strong class="balance-value">¥{{ balance }}</strong>
        <el-button type="primary" round @click="showRecharge = true">充值</el-button>
      </el-card>

      <div class="history-main">
        <el-tabs v-model="activeType" @tab-change="fetchData">
          <el-tab-pane label="全部" name="" />
          <el-tab-pane label="消费记录" name="booking" />
          <el-tab-pane label="充值记录" name="recharge" />
          <el-tab-pane label="退款记录" name="refund" />
        </el-tabs>

        <el-card shadow="never">
          <el-table :data="list" v-loading="loading" empty-text="暂无记录">
            <el-table-column label="类型" width="100">
              <template #default="{ row }">
                <el-tag
                  :type="{ recharge: 'success', booking: 'warning', refund: 'info' }[row.type] || 'info'"
                  effect="light"
                  round
                  size="small"
                >
                  {{ { recharge: "充值", booking: "消费", refund: "退款" }[row.type] || row.type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="金额" width="160">
              <template #default="{ row }">
                <span class="amount">¥{{ row.amount }}</span>
                <span v-if="row.bonus && Number(row.bonus) > 0" class="bonus-text">
                  +送 ¥{{ row.bonus }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="方式" width="110">
              <template #default="{ row }">
                {{ { balance: "余额", wechat: "微信", alipay: "支付宝" }[row.method] }}
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
            <el-table-column label="时间" min-width="170">
              <template #default="{ row }">
                {{ row.created_at?.slice(0, 19).replace("T", " ") }}
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            v-model:current-page="query.page"
            :total="total"
            layout="total, prev, pager, next"
            @current-change="fetchData"
            class="table-footer"
          />
        </el-card>
      </div>
    </div>

    <el-dialog v-model="showRecharge" title="余额充值" width="380px">
      <el-form :model="rechargeForm" label-width="80px">
        <el-form-item label="充值金额">
          <el-input-number v-model="rechargeForm.amount" :min="1" :step="50" style="width: 210px" />
        </el-form-item>
        <el-form-item label="支付方式">
          <el-radio-group v-model="rechargeForm.method">
            <el-radio value="wechat">微信支付</el-radio>
            <el-radio value="alipay">支付宝</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <div class="recharge-bonus">
        <span>充值赠送</span>
        <strong>¥{{ rechargeBonus }}，到账 ¥{{ rechargeBonus + rechargeForm.amount }}</strong>
      </div>
      <template #footer>
        <el-button @click="showRecharge = false">取消</el-button>
        <el-button type="primary" :loading="recharging" @click="handleRecharge">确认充值</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue"
import { ElMessage } from "element-plus"
import { Wallet } from "@element-plus/icons-vue"
import { paymentApi } from "@/api/payments"
import { getRechargeBonus } from "@/utils/recharge"
import { useUserStore } from "@/store"

const userStore = useUserStore()
const list = ref([])
const total = ref(0)
const loading = ref(false)
const showRecharge = ref(false)
const recharging = ref(false)
const activeType = ref("")
const balance = ref(userStore.userInfo?.balance || 0)
const rechargeForm = reactive({ amount: 100, method: "wechat" })
const rechargeBonus = computed(() => getRechargeBonus(rechargeForm.amount))

const query = reactive({ page: 1, page_size: 20 })

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

async function handleRecharge() {
  recharging.value = true
  try {
    const res = await paymentApi.recharge({
      amount: rechargeForm.amount,
      method: rechargeForm.method,
    })
    balance.value = res.data.balance
    userStore.userInfo.balance = res.data.balance
    const bonus = Number(res.data.bonus || 0)
    ElMessage.success(
      bonus > 0
        ? `充值成功，赠送 ¥${bonus}，余额 ¥${res.data.balance}`
        : `充值成功，余额 ¥${res.data.balance}`
    )
    showRecharge.value = false
    fetchData()
  } catch {
    ElMessage.error("充值失败")
  } finally {
    recharging.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.payment-history {
  width: 100%;
  max-width: 1080px;
  margin: 0 auto;
}

.history-layout {
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr);
  gap: 16px;
  align-items: start;
}

.balance-card {
  position: sticky;
  top: 84px;
  text-align: center;
}

.balance-card :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 24px 18px;
}

.balance-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 14px;
  color: var(--mui-primary);
  background: var(--mui-primary-soft);
}

.balance-label {
  color: var(--mui-muted);
  font-size: 13px;
  font-weight: 600;
}

.balance-value {
  color: var(--mui-primary);
  font-size: 28px;
  font-weight: 800;
}

.history-main {
  min-width: 0;
}

.amount {
  color: var(--mui-primary);
  font-weight: 800;
}

.bonus-text {
  margin-left: 6px;
  color: var(--mui-success);
  font-size: 12px;
  font-weight: 700;
}

.recharge-bonus {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 6px;
  padding: 10px 14px;
  border-radius: 10px;
  color: var(--mui-muted);
  background: #f8fafc;
  font-size: 13px;
}

.recharge-bonus strong {
  color: var(--mui-primary);
  font-weight: 800;
}

@media (max-width: 800px) {
  .history-layout {
    grid-template-columns: 1fr;
  }

  .balance-card {
    position: static;
  }
}
</style>
