<template>
  <div class="orders-page">
    <div class="page-header">
      <h2>我的订单</h2>
      <p>查看预约记录并完成支付</p>
    </div>

    <div class="orders-layout">
      <el-card shadow="never" class="balance-card">
        <span class="balance-icon"><el-icon :size="24"><Wallet /></el-icon></span>
        <span class="balance-label">当前余额</span>
        <strong class="balance-value">¥{{ userStore.userInfo?.balance || 0 }}</strong>
        <el-button type="primary" round @click="showRecharge = true">充值</el-button>
      </el-card>

      <div class="orders-main">
        <el-tabs v-model="activeTab" @tab-change="fetchData">
          <el-tab-pane label="全部" name="" />
          <el-tab-pane label="待支付" name="pending" />
          <el-tab-pane label="已支付" name="paid" />
          <el-tab-pane label="已取消" name="cancelled" />
        </el-tabs>

        <el-card shadow="never">
          <el-table :data="list" v-loading="loading" empty-text="暂无订单">
            <el-table-column prop="venue_name" label="场馆" min-width="140" />
            <el-table-column prop="court_name" label="场地" width="90" />
            <el-table-column prop="date" label="日期" width="110" />
            <el-table-column prop="time_slot_display" label="时段" width="110" />
            <el-table-column label="金额" width="100">
              <template #default="{ row }">
                <span class="amount">¥{{ row.amount }}</span>
              </template>
            </el-table-column>
            <el-table-column label="折扣" width="90">
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
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag
                  :type="{ pending: 'warning', paid: 'success', cancelled: 'info' }[row.status]"
                  effect="light"
                  round
                  size="small"
                >
                  {{ { pending: '待支付', paid: '已支付', cancelled: '已取消' }[row.status] }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="签到" width="90">
              <template #default="{ row }">
                <template v-if="row.status === 'paid'">
                  <el-tag v-if="row.checked_in" type="success" effect="plain" round size="small">已签到</el-tag>
                  <el-tag v-else type="info" effect="plain" round size="small">待使用</el-tag>
                </template>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button
                  v-if="row.status === 'pending'"
                  size="small"
                  type="success"
                  @click="handlePay(row)"
                >
                  支付
                </el-button>
                <el-button v-if="row.status === 'pending'" size="small" @click="handleCancel(row)">
                  取消
                </el-button>
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
            <el-radio value="wechat">微信</el-radio>
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

    <el-dialog v-model="showPay" title="确认支付" width="380px">
      <div class="pay-summary">
        <span>订单金额</span>
        <strong>¥{{ payForm.amount }}</strong>
      </div>
      <el-radio-group v-model="payForm.method" class="pay-methods">
        <el-radio value="balance" border>余额支付 (¥{{ userStore.userInfo?.balance || 0 }})</el-radio>
        <el-radio value="wechat" border>微信支付</el-radio>
        <el-radio value="alipay" border>支付宝</el-radio>
      </el-radio-group>
      <template #footer>
        <el-button @click="showPay = false">取消</el-button>
        <el-button type="primary" :loading="paying" @click="confirmPay">确认支付</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import { Wallet } from "@element-plus/icons-vue"
import { bookingApi } from "@/api/bookings"
import { paymentApi } from "@/api/payments"
import { getRechargeBonus } from "@/utils/recharge"
import { useUserStore } from "@/store"

const userStore = useUserStore()
const list = ref([])
const total = ref(0)
const loading = ref(false)
const showRecharge = ref(false)
const recharging = ref(false)
const showPay = ref(false)
const paying = ref(false)
const activeTab = ref("")
const query = reactive({ page: 1, page_size: 20 })
const rechargeForm = reactive({ amount: 100, method: "wechat" })
const payForm = reactive({ bookingId: null, amount: 0, method: "balance" })

const rechargeBonus = computed(() => getRechargeBonus(rechargeForm.amount))

const discountText = (rate) => {
  const value = Number(rate)
  if (value >= 1) return "原价"
  return `${Math.round(value * 100)}折`
}

async function fetchData() {
  loading.value = true
  try {
    const params = { page: query.page, page_size: query.page_size }
    if (activeTab.value) params.status = activeTab.value
    const res = await bookingApi.my(params)
    list.value = res.results || []
    total.value = res.count || 0
  } catch {
    ElMessage.error("获取订单失败")
  } finally {
    loading.value = false
  }
}

async function handleRecharge() {
  recharging.value = true
  try {
    const res = await paymentApi.recharge(rechargeForm)
    userStore.userInfo.balance = res.data.balance
    const bonus = Number(res.data.bonus || 0)
    ElMessage.success(
      bonus > 0
        ? `充值成功，赠送 ¥${bonus}，余额 ¥${res.data.balance}`
        : `充值成功，余额 ¥${res.data.balance}`
    )
    showRecharge.value = false
  } catch {
    ElMessage.error("充值失败")
  } finally {
    recharging.value = false
  }
}

function handlePay(row) {
  payForm.bookingId = row.id
  payForm.amount = row.amount
  payForm.method = "balance"
  showPay.value = true
}

async function confirmPay() {
  paying.value = true
  try {
    const res = await paymentApi.pay({
      booking_id: payForm.bookingId,
      method: payForm.method,
    })
    userStore.userInfo.balance = res.data.balance
    ElMessage.success("支付成功")
    showPay.value = false
    fetchData()
  } catch {
    ElMessage.error("支付失败，请检查余额")
  } finally {
    paying.value = false
  }
}

async function handleCancel(row) {
  try {
    await ElMessageBox.confirm("确定取消该订单？", "取消确认", { type: "warning" })
    await bookingApi.cancel(row.id)
    ElMessage.success("已取消")
    fetchData()
  } catch {
    // canceled or handled
  }
}

onMounted(fetchData)
</script>

<style scoped>
.orders-page {
  width: 100%;
  max-width: 1080px;
  margin: 0 auto;
}

.orders-layout {
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

.orders-main {
  min-width: 0;
}

.amount {
  color: var(--mui-primary);
  font-weight: 800;
}

.discount-text {
  color: var(--mui-primary);
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

.pay-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
  padding: 14px;
  border-radius: 12px;
  background: #f8fafc;
}

.pay-summary span {
  color: var(--mui-muted);
  font-weight: 600;
}

.pay-summary strong {
  color: var(--mui-primary);
  font-size: 24px;
  font-weight: 800;
}

.pay-methods {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 8px;
}

.pay-methods .el-radio {
  margin-right: 0;
  height: auto;
  padding: 10px 14px;
}

@media (max-width: 800px) {
  .orders-layout {
    grid-template-columns: 1fr;
  }

  .balance-card {
    position: static;
  }
}
</style>
