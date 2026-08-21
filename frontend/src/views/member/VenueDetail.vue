<template>
  <div class="venue-detail">
    <div class="detail-toolbar">
      <el-button round @click="$router.push('/venues')">
        <el-icon class="el-icon--left"><Back /></el-icon>返回场馆列表
      </el-button>
      <div v-if="venue" class="toolbar-title">
        <strong>{{ venue.name }}</strong>
        <span>场馆详情</span>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <template v-else-if="venue">
      <el-card shadow="never" class="info-card">
        <div class="info-card-main">
          <span class="info-icon">
            <el-icon :size="26"><OfficeBuilding /></el-icon>
          </span>
          <div class="info-copy">
            <h2>{{ venue.name }}</h2>
            <div class="info-items">
              <span><el-icon><Location /></el-icon>{{ venue.address || "暂无地址" }}</span>
              <span><el-icon><Phone /></el-icon>{{ venue.phone || "暂无电话" }}</span>
            </div>
          </div>
          <el-tag v-if="venue.is_active" type="success" effect="light" round>营业中</el-tag>
          <el-tag v-else type="info" effect="light" round>已停用</el-tag>
        </div>
      </el-card>

      <el-card shadow="never" class="booking-card">
        <template #header>
          <div class="card-header-title">
            <span>预约信息</span>
            <span class="header-hint">选择日期与场地后预约时段</span>
          </div>
        </template>

        <div class="booking-form-row">
          <div class="field-label">预约日期</div>
          <el-date-picker
            v-model="bookDate"
            type="date"
            value-format="YYYY-MM-DD"
            :disabled-date="disabledDate"
            placeholder="选择日期"
            style="width: 220px"
          />
        </div>

        <div v-if="!bookDate" class="booking-empty">
          <el-icon :size="28"><Calendar /></el-icon>
          <span>请先选择预约日期</span>
        </div>

        <template v-else>
          <div class="section-title">
            <span>选择场地</span>
            <span class="section-hint">{{ venue.courts.length }} 个场地</span>
          </div>
          <div class="court-list">
            <el-tag
              v-for="court in venue.courts"
              :key="court.id"
              :type="selectedCourt?.id === court.id ? 'primary' : 'info'"
              effect="light"
              round
              size="large"
              class="court-chip"
              @click="selectedCourt = court"
            >
              {{ court.name }}
            </el-tag>
            <div v-if="venue.courts.length === 0" class="booking-empty compact">
              <el-icon :size="24"><OfficeBuilding /></el-icon>
              <span>暂无场地</span>
            </div>
          </div>

          <div class="section-title slot-title">
            <span>时段</span>
            <span v-if="selectedCourt" class="selected-court">已选 {{ selectedCourt.name }}</span>
            <span v-else class="section-hint">请先选择场地</span>
          </div>
          <el-table
            v-if="venue.time_slots.length"
            :data="venue.time_slots"
            v-loading="bookingLoading"
            size="default"
          >
            <el-table-column prop="display" label="时段" min-width="120" />
            <el-table-column label="价格" width="150">
              <template #default="{ row }">
                <div v-if="memberPrice(row) < Number(row.price)" class="price-wrap">
                  <span class="original-price">¥{{ row.price }}</span>
                  <strong class="member-price">¥{{ memberPrice(row) }}</strong>
                </div>
                <span v-else class="price-text">¥{{ row.price }}</span>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="110">
              <template #default="{ row }">
                <el-tag v-if="isSlotBooked(row)" type="danger" effect="light" round>已预约</el-tag>
                <el-tag v-else type="success" effect="light" round>可预约</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="right">
              <template #default="{ row }">
                <el-button
                  type="primary"
                  size="small"
                  :disabled="isSlotBooked(row) || !selectedCourt"
                  @click="handleBook(row)"
                >
                  预约
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <div v-else class="booking-empty compact">
            <el-icon :size="24"><Clock /></el-icon>
            <span>暂无时段</span>
          </div>
        </template>
      </el-card>
    </template>

    <div v-else class="booking-empty full">
      <el-icon :size="36"><OfficeBuilding /></el-icon>
      <span>场馆不存在</span>
    </div>

    <el-dialog
      v-model="showPayDialog"
      title="订单支付"
      width="420px"
      :close-on-click-modal="false"
      @close="handlePayDialogClose"
    >
      <div class="pay-summary">
        <div class="pay-summary-head">
          <span class="pay-icon"><el-icon :size="24"><Wallet /></el-icon></span>
          <div>
            <strong>{{ payForm.venueName }}</strong>
            <span>{{ payForm.courtName }} · {{ payForm.date }}</span>
          </div>
        </div>
        <div class="pay-detail-row">
          <span>时段</span>
          <strong>{{ payForm.display }}</strong>
        </div>
        <div
          v-if="payForm.originalAmount && Number(payForm.discountRate) < 1"
          class="pay-detail-row"
        >
          <span>原价</span>
          <span class="original-price">¥{{ payForm.originalAmount }}</span>
        </div>
        <div
          v-if="payForm.discountRate && Number(payForm.discountRate) < 1"
          class="pay-detail-row discount-row"
        >
          <span>会员折扣</span>
          <strong>{{ discountText(payForm.discountRate) }}</strong>
        </div>
        <div class="pay-detail-row amount-row">
          <span>支付金额</span>
          <strong>¥{{ payForm.amount }}</strong>
        </div>
      </div>

      <div class="pay-methods-title">选择支付方式</div>
      <el-radio-group v-model="payForm.method" class="pay-methods">
        <el-radio value="balance" border>
          余额支付 (¥{{ userStore.userInfo?.balance || 0 }})
        </el-radio>
        <el-radio value="wechat" border>微信支付</el-radio>
        <el-radio value="alipay" border>支付宝</el-radio>
      </el-radio-group>

      <template #footer>
        <el-button @click="handleLaterPay">稍后支付</el-button>
        <el-button type="primary" :loading="paying" @click="handlePay">立即支付</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { ElMessage, ElMessageBox } from "element-plus"
import {
  Location,
  Phone,
  Loading,
  Back,
  OfficeBuilding,
  Calendar,
  Clock,
  Wallet,
} from "@element-plus/icons-vue"
import { venueApi } from "@/api/venues"
import { bookingApi } from "@/api/bookings"
import { paymentApi } from "@/api/payments"
import { useUserStore } from "@/store"

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const venue = ref(null)
const loading = ref(true)
const bookingLoading = ref(false)
const bookDate = ref("")
const selectedCourt = ref(null)
const bookedSlots = ref([])
const showPayDialog = ref(false)
const paying = ref(false)
const payForm = ref({
  bookingId: null,
  amount: 0,
  method: "balance",
  date: "",
  display: "",
  courtName: "",
  venueName: "",
  originalAmount: null,
  discountRate: 1,
})

function memberPrice(row) {
  const price = Number(row.price)
  const discounted = Number(row.discounted_price ?? row.price)
  return discounted > 0 && discounted < price ? discounted : price
}

function discountText(rate) {
  const value = Number(rate)
  if (value >= 1) return "原价"
  return `${Math.round(value * 100)}折`
}

function disabledDate(time) {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return time.getTime() < today.getTime()
}

async function fetchVenue() {
  try {
    const res = await venueApi.detail(route.params.id)
    venue.value = res
  } catch {
    ElMessage.error("获取场馆信息失败")
  } finally {
    loading.value = false
  }
}

async function fetchBookings() {
  if (!bookDate.value || !venue.value) return
  bookingLoading.value = true
  try {
    const res = await bookingApi.list({
      date: bookDate.value,
      venue: venue.value.id,
      page_size: 200,
    })
    bookedSlots.value = res.results || []
  } catch {
    bookedSlots.value = []
  } finally {
    bookingLoading.value = false
  }
}

function isSlotBooked(slot) {
  const courtId = selectedCourt.value?.id
  if (!courtId) return false
  return bookedSlots.value.some(
    (b) => b.court === courtId && b.time_slot === slot.id && b.status !== "cancelled"
  )
}

async function handleBook(slot) {
  if (!selectedCourt.value) {
    ElMessage.warning("请先选择一个场地")
    return
  }
  const courtId = selectedCourt.value.id
  const date = bookDate.value
  if (isSlotBooked(slot)) {
    ElMessage.warning("该时段已被预约")
    return
  }
  try {
    await ElMessageBox.confirm(
      "确认预约「" +
        venue.value.name +
        " - " +
        selectedCourt.value.name +
        "」\n日期: " +
        date +
        "\n时段: " +
        slot.display +
        "\n金额: ¥" +
        memberPrice(slot),
      "预约确认",
      { confirmButtonText: "确认", cancelButtonText: "取消", type: "info" }
    )
  } catch {
    return
  }
  try {
    const booking = await bookingApi.create({
      court: courtId,
      date: date,
      time_slot: slot.id,
    })
    payForm.value = {
      bookingId: booking.id,
      amount: Number(booking.amount || slot.price),
      method: "balance",
      date,
      display: slot.display,
      courtName: selectedCourt.value.name,
      venueName: venue.value.name,
      originalAmount: booking.original_amount || slot.price,
      discountRate: booking.discount_rate || 1,
    }
    showPayDialog.value = true
    ElMessage.success("预约成功，请完成支付")
    fetchBookings()
  } catch (e) {
    const msg = e?.response?.data?.[0] || e?.response?.data?.message || "预约失败"
    ElMessage.error(msg)
  }
}

function handleLaterPay() {
  showPayDialog.value = false
}

function handlePayDialogClose() {
  router.push("/orders")
}

async function handlePay() {
  if (!payForm.value.bookingId) return
  paying.value = true
  try {
    const res = await paymentApi.pay({
      booking_id: payForm.value.bookingId,
      method: payForm.value.method,
    })
    if (userStore.userInfo) {
      userStore.userInfo.balance = res.data.balance
      userStore.setUserInfo(userStore.userInfo)
    }
    ElMessage.success("支付成功")
    showPayDialog.value = false
    fetchBookings()
  } catch (e) {
    const msg = e?.response?.data?.message || "支付失败，请检查余额"
    ElMessage.error(msg)
  } finally {
    paying.value = false
  }
}

onMounted(fetchVenue)
</script>

<style scoped>
.venue-detail {
  width: 100%;
  max-width: 1080px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
}

.toolbar-title {
  display: flex;
  flex-direction: column;
}

.toolbar-title strong {
  color: var(--mui-text);
  font-size: 18px;
  font-weight: 800;
}

.toolbar-title span {
  color: var(--mui-muted);
  font-size: 12px;
}

.loading-state,
.booking-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  min-height: 240px;
  color: var(--mui-muted);
}

.info-card-main {
  display: flex;
  align-items: center;
  gap: 16px;
}

.info-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 16px;
  color: var(--mui-primary);
  background: var(--mui-primary-soft);
  flex: 0 0 56px;
}

.info-copy {
  flex: 1;
  min-width: 0;
}

.info-copy h2 {
  margin: 0 0 8px;
  color: var(--mui-text);
  font-size: 22px;
  font-weight: 800;
}

.info-items {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 20px;
}

.info-items span {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--mui-muted);
  font-size: 13px;
}

.card-header-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.card-header-title > span:first-child {
  font-size: 15px;
}

.header-hint,
.section-hint,
.selected-court {
  color: var(--mui-muted);
  font-size: 12px;
  font-weight: 600;
}

.selected-court {
  color: var(--mui-primary);
}

.booking-form-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.field-label,
.section-title {
  color: var(--mui-text);
  font-size: 14px;
  font-weight: 800;
}

.section-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin: 20px 0 12px;
}

.court-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.court-chip {
  cursor: pointer;
  transition: transform 0.16s ease;
}

.court-chip:hover {
  transform: translateY(-2px);
}

.slot-title {
  margin-top: 28px;
}

.price-text {
  color: var(--mui-primary);
  font-weight: 800;
}

.price-wrap {
  display: flex;
  align-items: center;
  gap: 6px;
}

.original-price {
  color: #94a3b8;
  font-size: 12px;
  text-decoration: line-through;
}

.member-price {
  color: var(--mui-primary);
  font-weight: 800;
}

.discount-row strong {
  color: var(--mui-primary);
}

.booking-empty.compact {
  min-height: 120px;
}

.booking-empty.full {
  min-height: 320px;
}

.pay-summary {
  padding: 16px;
  border: 1px solid var(--mui-border);
  border-radius: 14px;
  background: #f8fafc;
}

.pay-summary-head {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--mui-border-soft);
}

.pay-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  color: var(--mui-primary);
  background: var(--mui-primary-soft);
  flex: 0 0 44px;
}

.pay-summary-head div {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.pay-summary-head strong {
  color: var(--mui-text);
  font-size: 15px;
  font-weight: 800;
}

.pay-summary-head span {
  margin-top: 4px;
  color: var(--mui-muted);
  font-size: 13px;
}

.pay-detail-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 14px;
  color: var(--mui-muted);
  font-size: 13px;
}

.pay-detail-row strong {
  color: var(--mui-text);
  font-size: 14px;
}

.amount-row strong {
  color: var(--mui-primary);
  font-size: 22px;
  font-weight: 800;
}

.pay-methods-title {
  margin: 18px 0 10px;
  color: var(--mui-text);
  font-size: 14px;
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

@media (max-width: 640px) {
  .info-card-main {
    flex-wrap: wrap;
  }

  .booking-form-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
