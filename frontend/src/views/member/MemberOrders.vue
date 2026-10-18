<template>
  <div class="orders-page">
    <header class="page-header">
      <h2>我的订单</h2>
      <p>预约记录、支付与取消都在这一页完成，金额是折后实付</p>
    </header>

    <section class="surface orders-panel">
      <header class="panel-head">
        <h3>订单流水</h3>
        <div class="head-right">
          <span class="head-balance">余额 <b class="mono">¥{{ money(userStore.userInfo?.balance) }}</b></span>
          <el-button type="primary" class="head-cta" @click="showRecharge = true">
            <el-icon class="el-icon--left"><Wallet /></el-icon>充值
          </el-button>
        </div>
      </header>

      <div class="panel-filter">
        <el-radio-group v-model="activeTab" @change="fetchData">
          <el-radio-button value="">全部</el-radio-button>
          <el-radio-button value="pending">待支付</el-radio-button>
          <el-radio-button value="paid">已支付</el-radio-button>
          <el-radio-button value="cancelled">已取消</el-radio-button>
        </el-radio-group>
        <span class="panel-count mono">{{ total }} 笔</span>
      </div>

      <el-skeleton v-if="loading && !list.length" :rows="4" animated class="panel-skeleton" />

      <template v-else>
        <ul v-if="list.length" class="order-list" :class="{ 'is-busy': loading }">
          <li v-for="row in list" :key="row.id" class="order">
            <div class="order-info">
              <div class="order-head">
                <h4>{{ row.venue_name }}</h4>
                <el-tag :type="statusTag(row.status)" effect="light" round size="small">
                  {{ statusLabel(row.status) }}
                </el-tag>
                <el-tag
                  v-if="row.status === 'paid'"
                  :type="row.checked_in ? 'success' : 'info'"
                  effect="plain"
                  round
                  size="small"
                >
                  {{ row.checked_in ? '已签到' : '待使用' }}
                </el-tag>
              </div>

              <p class="order-meta mono">
                <span>{{ row.court_name }}</span>
                <span>{{ row.date }}</span>
                <span>{{ row.time_slot_display }}</span>
                <span class="dim">#{{ row.id }}</span>
              </p>
            </div>

            <div class="order-price">
              <strong class="price-final mono">¥{{ money(row.amount) }}</strong>
              <span v-if="hasDiscount(row)" class="price-calc mono">
                原价 ¥{{ money(row.original_amount) }} · {{ discountText(row.discount_rate) }}
              </span>
            </div>

            <div class="order-actions">
              <template v-if="row.status === 'pending'">
                <el-button type="primary" @click="handlePay(row)">支付</el-button>
                <el-button @click="handleCancel(row)">取消</el-button>
              </template>
              <template v-else-if="row.status === 'paid' && row.checked_in">
                <el-button @click="openReview(row)">评价</el-button>
              </template>
              <template v-else-if="row.status === 'paid'">
                <el-tag v-if="row.cancellation_status === 'pending'" type="warning" effect="light" round>退场审批中</el-tag>
                <el-tag v-else-if="row.cancellation_status === 'approved'" type="primary" effect="light" round>待退款</el-tag>
                <el-tag v-else-if="row.cancellation_status === 'refunded'" type="success" effect="light" round>已退款</el-tag>
                <el-tag v-else-if="row.cancellation_status === 'rejected'" type="danger" effect="light" round>退场被驳回</el-tag>
                <el-button v-else-if="row.cancel_window === 'free'" @click="handleCancel(row)">取消预约</el-button>
                <el-button v-else-if="row.cancel_window === 'request'" type="warning" @click="handleRequestCancel(row)">申请退场</el-button>
              </template>
            </div>
          </li>
        </ul>

        <div v-else class="empty-state">
          <strong>还没有这类订单</strong>
          <span>挑一座球馆、选一个时段下单，记录就会出现在这里。</span>
        </div>
      </template>

      <el-pagination
        v-model:current-page="query.page"
        :total="total"
        :page-size="query.page_size"
        layout="prev, pager, next"
        @current-change="fetchData"
        class="table-footer"
      />
    </section>

    <el-dialog v-model="showRecharge" title="余额充值" width="440px" class="narrow-dialog">
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

      <div class="receipt">
        <span class="receipt__label">实付</span>
        <strong class="receipt__pay mono">¥{{ money(rechargeForm.amount) }}</strong>
        <span class="receipt__arrow" aria-hidden="true">→</span>
        <span class="receipt__label">到账</span>
        <strong class="receipt__get mono">¥{{ money(rechargeCredit) }}</strong>
      </div>

      <template #footer>
        <el-button @click="showRecharge = false">取消</el-button>
        <el-button type="primary" :loading="recharging" @click="handleRecharge">确认充值</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showPay" title="确认支付" width="400px" class="narrow-dialog">
      <div class="pay-summary">
        <span>订单金额</span>
        <strong class="mono">¥{{ money(payForm.amount) }}</strong>
      </div>
      <el-radio-group v-model="payForm.method" class="pay-methods">
        <el-radio value="balance" border>
          余额支付（可用 <span class="mono">¥{{ money(userStore.userInfo?.balance) }}</span>）
        </el-radio>
        <el-radio value="wechat" border>微信支付</el-radio>
        <el-radio value="alipay" border>支付宝</el-radio>
      </el-radio-group>
      <template #footer>
        <el-button @click="showPay = false">取消</el-button>
        <el-button type="primary" :loading="paying" @click="confirmPay">确认支付</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showReview" title="订单评价" width="420px" class="narrow-dialog">
      <div class="review-order mono dim">#{{ reviewForm.bookingId }} · 已签到订单</div>
      <el-rate v-model="reviewForm.rating" />
      <el-input
        v-model="reviewForm.content"
        type="textarea"
        :rows="3"
        maxlength="200"
        show-word-limit
        placeholder="场地、时段、服务体验怎么样？"
      />
      <template #footer>
        <el-button @click="showReview = false">取消</el-button>
        <el-button type="primary" :loading="reviewLoading" @click="submitReview">提交评价</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import { Wallet } from "@element-plus/icons-vue"
import api from "@/api"
import { bookingApi } from "@/api/bookings"
import { paymentApi } from "@/api/payments"
import { reviewApi } from "@/api/reviews"
import { getRechargeBonus, loadBonusTiers } from "@/utils/recharge"
import { money, discountText, bookingStatusTag as statusTag, bookingStatusLabel as statusLabel } from "@/utils/format"
import { useUserStore } from "@/store"

const userStore = useUserStore()
const list = ref([])
const total = ref(0)
const loading = ref(false)
const showRecharge = ref(false)
const recharging = ref(false)
const showPay = ref(false)
const paying = ref(false)
const showReview = ref(false)
const reviewLoading = ref(false)
const activeTab = ref("")
const query = reactive({ page: 1, page_size: 20 })
const rechargeForm = reactive({ amount: 100, method: "wechat" })
const payForm = reactive({ bookingId: null, amount: 0, method: "balance" })
const reviewForm = reactive({ bookingId: null, rating: 5, content: "" })

const rechargeBonus = computed(() => getRechargeBonus(rechargeForm.amount))
const rechargeCredit = computed(() => Number(rechargeForm.amount || 0) + rechargeBonus.value)

/** 有折扣（原价与实付不同）时才展示原价那一行 */
const hasDiscount = (row) => {
  const original = Number(row.original_amount || 0)
  return original > 0 && original !== Number(row.amount || 0)
}

async function fetchData() {
  loading.value = true
  try {
    const params = { page: query.page, page_size: query.page_size }
    if (activeTab.value) params.status = activeTab.value
    const res = await bookingApi.my(params)
    list.value = res.results || []
    total.value = res.count || 0
    // 拉取订单会触发到期退款的惰性处理，余额可能刚变——同步刷新，无需手动刷页面
    refreshBalance()
  } catch {
    ElMessage.error("获取订单失败")
  } finally {
    loading.value = false
  }
}

async function refreshBalance() {
  try {
    const res = await api.get("users/me/")
    if (res?.data) userStore.setUserInfo(res.data)
  } catch {
    // 静默：余额刷新失败不打断订单列表
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
    const res = await bookingApi.cancel(row.id)
    const refund = res?.data?.refund_amount
    if (refund && Number(refund) > 0) {
      // 退款已回到余额：同步刷新顶部余额显示，避免用户误以为没退钱
      if (res.data.balance != null) {
        userStore.userInfo.balance = res.data.balance
        userStore.setUserInfo(userStore.userInfo)
      }
      ElMessage.success(`已取消，退款 ¥${refund}`)
    } else {
      ElMessage.success("已取消")
    }
    fetchData()
  } catch {
    // canceled or handled
  }
}

async function handleRequestCancel(row) {
  try {
    await ElMessageBox.confirm(
      "退场申请将提交前台审批，审批通过后 5 分钟自动退款。确定申请？",
      "申请退场",
      { type: "warning", confirmButtonText: "提交申请", cancelButtonText: "取消" }
    )
    await bookingApi.requestCancel(row.id, { reason: "" })
    ElMessage.success("退场申请已提交，等待前台审批")
    fetchData()
  } catch {
    // canceled or handled
  }
}

function openReview(row) {
  reviewForm.bookingId = row.id
  reviewForm.rating = 5
  reviewForm.content = ""
  showReview.value = true
}

async function submitReview() {
  reviewLoading.value = true
  try {
    await reviewApi.create({
      booking: reviewForm.bookingId,
      rating: reviewForm.rating,
      content: reviewForm.content,
    })
    ElMessage.success("评价成功")
    showReview.value = false
    fetchData()
  } catch {
    // 拦截器已提示
  } finally {
    reviewLoading.value = false
  }
}

onMounted(() => {
  fetchData()
  loadBonusTiers()
})
</script>

<style scoped>
.orders-page {
  width: 100%;
  max-width: 1040px;
  margin: 0 auto;
  padding: 28px 24px 72px;
}

.orders-panel {
  display: flex;
  flex-direction: column;
}

/* ---------- 面板头 ---------- */

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-soft);
}

.panel-head h3 {
  margin: 0;
  font-size: var(--fs-14);
  font-weight: 700;
  color: var(--ink-1);
}

.head-right {
  display: flex;
  align-items: center;
  gap: 14px;
}

.head-balance {
  font-size: var(--fs-13);
  color: var(--ink-3);
  white-space: nowrap;
}

.head-balance b {
  font-size: var(--fs-14);
  font-weight: 800;
  color: var(--accent);
}

.head-cta {
  min-height: 40px;
}

/* ---------- 筛选 ---------- */

.panel-filter {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  flex-wrap: wrap;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border-soft);
}

.panel-count {
  font-size: var(--fs-12);
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--ink-4);
  white-space: nowrap;
}

.panel-skeleton {
  padding: 20px;
}

/* ---------- 订单行：用分隔线组织，不堆卡片 ---------- */

.order-list {
  margin: 0;
  padding: 0;
  list-style: none;
  transition: opacity var(--dur-2) var(--ease-out);
}

.order-list.is-busy {
  opacity: 0.55;
}

.order {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  align-items: center;
  gap: 10px 22px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-soft);
}

.order:last-child {
  border-bottom: 0;
}

.order-head {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.order-head h4 {
  margin: 0;
  font-size: var(--fs-16);
  font-weight: 800;
  color: var(--ink-1);
}

.order-meta {
  display: flex;
  align-items: center;
  gap: 8px 14px;
  flex-wrap: wrap;
  margin: 7px 0 0;
  font-size: var(--fs-12);
  color: var(--ink-3);
}

.order-meta .dim {
  color: var(--ink-4);
}

.order-price {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
  min-width: 132px;
}

.price-final {
  font-size: var(--fs-18);
  font-weight: 800;
  color: var(--ink-1);
}

.price-calc {
  font-size: var(--fs-11);
  color: var(--ink-3);
  white-space: nowrap;
}

.order-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  /* 定宽：让每一行的金额列右边缘对齐，不随按钮多少左右摆 */
  min-width: 150px;
}

.order-actions :deep(.el-button) {
  min-height: 40px;
  margin: 0;
}

/* ---------- 充值 / 支付弹窗 ---------- */

.receipt {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 8px 10px;
  padding: 12px 14px;
  border: 1px dashed var(--border-strong);
  border-radius: var(--radius);
  font-size: var(--fs-13);
}

.receipt__label {
  color: var(--ink-3);
}

.receipt__pay {
  font-size: var(--fs-16);
  font-weight: 800;
  color: var(--ink-1);
}

.receipt__arrow {
  color: var(--ink-4);
}

.receipt__get {
  font-size: var(--fs-16);
  font-weight: 800;
  color: var(--accent);
}

.pay-summary {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px 14px;
  border-radius: var(--radius);
  background: var(--sunken);
}

.pay-summary span {
  font-size: var(--fs-13);
  color: var(--ink-3);
}

.pay-summary strong {
  font-size: var(--fs-22);
  font-weight: 800;
  color: var(--ink-1);
}

.pay-methods {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 8px;
  width: 100%;
}

.pay-methods :deep(.el-radio) {
  height: auto;
  min-height: 44px;
  margin: 0;
  padding: 10px 14px;
}

/* ---------- 断点 ---------- */

@media (max-width: 720px) {
  .order {
    grid-template-columns: minmax(0, 1fr);
    gap: 12px;
  }

  .order-price {
    flex-direction: row;
    align-items: baseline;
    gap: 10px;
    min-width: 0;
  }

  .order-actions {
    justify-content: flex-start;
    min-width: 0;
  }

  .order-actions :deep(.el-button) {
    flex: 1 1 auto;
    min-height: 44px;
  }
}

@media (max-width: 640px) {
  .orders-page {
    padding: 20px 16px 56px;
  }

  .panel-head,
  .panel-filter {
    padding: 14px 16px;
  }

  .panel-filter :deep(.el-radio-group) {
    display: flex;
    width: 100%;
  }

  .panel-filter :deep(.el-radio-button) {
    flex: 1;
  }

  .panel-filter :deep(.el-radio-button__inner) {
    width: 100%;
    height: 44px;
    padding: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: var(--fs-12);
  }

  .order {
    padding: 15px 16px;
  }

  .table-footer {
    justify-content: center;
  }

  .table-footer :deep(.el-pagination) {
    flex-wrap: wrap;
    row-gap: 8px;
    justify-content: center;
  }
}
</style>

<style>
/* 弹窗挂在 body 上，作用域样式够不到；窄屏下不许横向溢出 */
.el-dialog.narrow-dialog {
  max-width: calc(100vw - 32px);
}
</style>
