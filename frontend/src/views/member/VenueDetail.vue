<template>
  <div class="venue-detail">
    <div class="detail-toolbar">
      <el-button round @click="$router.push('/venues')">
        <el-icon class="el-icon--left"><Back /></el-icon>返回场馆列表
      </el-button>
      <span v-if="venue" class="toolbar-title mono">{{ venue.name }}</span>
    </div>

    <div v-if="loading" class="detail-loading surface">
      <el-skeleton :rows="6" animated />
    </div>

    <template v-else-if="venue">
      <!-- 场馆抬头：名字、地址、电话，加一张球场细节图 -->
      <section class="venue-head surface">
        <div class="head-photo">
          <img
            src="/img/venue-detail-court.jpg"
            alt="室内球场白线与球网"
            loading="lazy"
            decoding="async"
            @error="hideBrokenImage"
          />
          <span class="head-photo-grade"></span>
        </div>

        <div class="head-copy">
          <div class="head-title">
            <h1>{{ venue.name }}</h1>
            <el-tag v-if="venue.is_active" type="success" effect="light" round>营业中</el-tag>
            <el-tag v-else type="info" effect="light" round>已停用</el-tag>
          </div>

          <div class="head-facts">
            <div>
              <span class="fact-label">地址</span>
              <span class="fact-value">{{ venue.address || '暂无地址' }}</span>
            </div>
            <div>
              <span class="fact-label">电话</span>
              <span class="fact-value mono">{{ venue.phone || '暂无电话' }}</span>
            </div>
            <div>
              <span class="fact-label">场地</span>
              <span class="fact-value mono">{{ courts.length }} 片</span>
            </div>
            <div>
              <span class="fact-label">时段</span>
              <span class="fact-value mono">{{ slots.length }} 个 / 天</span>
            </div>
          </div>
        </div>
      </section>

      <div class="detail-grid">
        <!-- 主区：场地 × 时段的印相板 -->
        <section class="board-panel surface">
          <header class="board-head">
            <div class="board-head-left">
              <h2>选时段</h2>
              <p>先选日期，再点棋盘上任意一格</p>
            </div>
            <div class="board-head-right">
              <el-date-picker
                v-model="bookDate"
                type="date"
                value-format="YYYY-MM-DD"
                :disabled-date="disabledDate"
                placeholder="选择日期"
                class="date-picker"
                @change="fetchBookings"
              />
            </div>
          </header>

          <div v-if="!bookDate" class="board-placeholder">
            <el-icon :size="26"><Calendar /></el-icon>
            <strong>请先选择预约日期</strong>
            <span>选完日期，这里会列出当天每片场地每个时段的可预约情况。</span>
          </div>

          <template v-else>
            <div class="board-legend">
              <span class="legend-item"><i class="dot dot--free"></i>可预约</span>
              <span class="legend-item"><i class="dot dot--booked"></i>已预约</span>
              <span v-if="discountRate < 1" class="legend-item legend-member">
                <i class="dot dot--member"></i>{{ levelLabel }} {{ discountText(discountRate) }}
              </span>
            </div>

            <div v-if="!courts.length || !slots.length" class="board-placeholder">
              <el-icon :size="26"><OfficeBuilding /></el-icon>
              <strong>这座球馆还没有开放场地或时段</strong>
              <span>请联系前台确认开放时间。</span>
            </div>

            <div v-else>
              <!-- 桌面：场地 × 时段 -->
              <div class="board" :style="boardStyle" v-loading="bookingLoading">
                <div class="board-corner mono">时段 \ 场地</div>
                <div v-for="c in courts" :key="'h' + c.id" class="board-court">{{ c.name }}</div>

                <template v-for="s in slots" :key="s.id">
                  <div class="board-time mono">{{ s.display }}</div>
                  <button
                    v-for="c in courts"
                    :key="c.id + '-' + s.id"
                    type="button"
                    class="cell"
                    :class="{ 'is-booked': isBooked(c, s) }"
                    :disabled="isBooked(c, s)"
                    :aria-label="`${c.name} ${s.display} ${isBooked(c, s) ? '已预约' : '可预约'}`"
                    @click="pick(c, s)"
                  >
                    <span v-if="isBooked(c, s)" class="cell-state">已订</span>
                    <span v-else class="cell-price mono">¥{{ memberPrice(s) }}</span>
                  </button>
                </template>
              </div>

              <!-- 手机：一个时段一行，可约的场地做成小块 -->
              <div class="board-list" v-loading="bookingLoading">
                <div v-for="s in slots" :key="'m' + s.id" class="slot-row">
                  <div class="slot-time mono">{{ s.display }}</div>
                  <div class="slot-courts">
                    <button
                      v-for="c in courts"
                      :key="'m' + c.id + '-' + s.id"
                      type="button"
                      class="court-chip"
                      :class="{ 'is-booked': isBooked(c, s) }"
                      :disabled="isBooked(c, s)"
                      @click="pick(c, s)"
                    >
                      <span class="chip-name">{{ c.name }}</span>
                      <span class="chip-price mono">{{ isBooked(c, s) ? '已订' : '¥' + memberPrice(s) }}</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </section>

        <!-- 侧栏：照片 + 会员小票 -->
        <aside class="detail-side">
          <div class="side-photo surface">
            <img
              src="/img/venue-detail-racket.jpg"
              alt="球拍与羽毛球特写"
              loading="lazy"
              decoding="async"
              @error="hideBrokenImage"
            />
            <span class="side-photo-grade"></span>
          </div>

          <section class="receipt surface">
            <h3 class="receipt-title">{{ levelLabel }}</h3>
            <div class="receipt-row">
              <span>场地折扣</span>
              <strong>{{ discountText(discountRate) }}</strong>
            </div>
            <div class="receipt-row">
              <span>账户余额</span>
              <strong class="mono">¥{{ Number(userStore.userInfo?.balance || 0).toFixed(2) }}</strong>
            </div>
            <hr class="hairline" />
            <p class="receipt-note">
              {{
                discountRate < 1
                  ? '折后价就是棋盘上显示的价格，折扣在下单时写进订单快照，之后等级变化不影响已生成的订单。'
                  : '累计消费满 ¥500 升银卡（95 折），满 ¥2000 升金卡（90 折）。'
              }}
            </p>
          </section>
        </aside>
      </div>
    </template>

    <div v-else class="surface empty-state">
      <strong>场馆不存在</strong>
      <span>它可能已经被删除，或者链接里的编号不对。</span>
      <el-button round @click="$router.push('/venues')">回到场馆列表</el-button>
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
          <span class="pay-icon"><el-icon :size="22"><Wallet /></el-icon></span>
          <div>
            <strong>{{ payForm.venueName }}</strong>
            <span>{{ payForm.courtName }} · {{ payForm.date }}</span>
          </div>
        </div>
        <div class="pay-detail-row">
          <span>时段</span>
          <strong class="mono">{{ payForm.display }}</strong>
        </div>
        <div
          v-if="payForm.originalAmount && Number(payForm.discountRate) < 1"
          class="pay-detail-row"
        >
          <span>原价</span>
          <span class="original-price mono">¥{{ payForm.originalAmount }}</span>
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
          <strong class="mono">¥{{ payForm.amount }}</strong>
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
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Back, OfficeBuilding, Calendar, Wallet } from '@element-plus/icons-vue'
import { venueApi } from '@/api/venues'
import { bookingApi } from '@/api/bookings'
import { paymentApi } from '@/api/payments'
import { useUserStore } from '@/store'
import { hideBrokenImage } from '@/utils/venueVisual'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const venue = ref(null)
const loading = ref(true)
const bookingLoading = ref(false)
const bookDate = ref('')
const selectedCourt = ref(null)
const bookedSlots = ref([])
const showPayDialog = ref(false)
const paying = ref(false)
const payForm = ref({
  bookingId: null,
  amount: 0,
  method: 'balance',
  date: '',
  display: '',
  courtName: '',
  venueName: '',
  originalAmount: null,
  discountRate: 1,
})

const courts = computed(() => venue.value?.courts || [])
const slots = computed(() => (venue.value?.time_slots || []).filter((s) => s.is_active !== false))
const boardStyle = computed(() => ({ '--cols': Math.max(courts.value.length, 1) }))

const discountRate = computed(() => Number(userStore.userInfo?.discount_rate ?? 1) || 1)
const levelLabel = computed(() => {
  const map = { normal: '普通会员', silver: '银卡会员', gold: '金卡会员' }
  return map[userStore.userInfo?.level] || '普通会员'
})

function memberPrice(row) {
  const price = Number(row.price)
  const discounted = Number(row.discounted_price ?? row.price)
  return discounted > 0 && discounted < price ? discounted : price
}

function discountText(rate) {
  const value = Number(rate)
  if (value >= 1) return '原价'
  return `${Math.round(value * 100)}折`
}

function disabledDate(time) {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return time.getTime() < today.getTime()
}

/** 某片场地某个时段是否已经被占 */
function isBooked(court, slot) {
  const courtId = court?.id
  if (!courtId) return false
  return bookedSlots.value.some((o) => o.court_id === courtId && o.time_slot_id === slot.id)
}

/** 棋盘上点一格：等价于「选中这片场地 + 预约这个时段」 */
function pick(court, slot) {
  if (isBooked(court, slot)) return
  selectedCourt.value = court
  handleBook(slot)
}

async function fetchVenue() {
  try {
    const res = await venueApi.detail(route.params.id)
    venue.value = res
  } catch {
    ElMessage.error('获取场馆信息失败')
  } finally {
    loading.value = false
  }
}

async function fetchBookings() {
  if (!bookDate.value || !venue.value) return
  bookingLoading.value = true
  try {
    const res = await venueApi.availability(venue.value.id, { date: bookDate.value })
    bookedSlots.value = res.occupied || []
  } catch {
    bookedSlots.value = []
  } finally {
    bookingLoading.value = false
  }
}

function isSlotBooked(slot) {
  return isBooked(selectedCourt.value, slot)
}

async function handleBook(slot) {
  if (!selectedCourt.value) {
    ElMessage.warning('请先选择一个场地')
    return
  }
  const courtId = selectedCourt.value.id
  const date = bookDate.value
  if (isSlotBooked(slot)) {
    ElMessage.warning('该时段已被预约')
    return
  }
  try {
    await ElMessageBox.confirm(
      '确认预约「' +
        venue.value.name +
        ' - ' +
        selectedCourt.value.name +
        '」\n日期: ' +
        date +
        '\n时段: ' +
        slot.display +
        '\n金额: ¥' +
        memberPrice(slot),
      '预约确认',
      { confirmButtonText: '确认', cancelButtonText: '取消', type: 'info' }
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
      method: 'balance',
      date,
      display: slot.display,
      courtName: selectedCourt.value.name,
      venueName: venue.value.name,
      originalAmount: booking.original_amount || slot.price,
      discountRate: booking.discount_rate || 1,
    }
    showPayDialog.value = true
    ElMessage.success('预约成功，请完成支付')
    fetchBookings()
  } catch (e) {
    const msg = e?.response?.data?.[0] || e?.response?.data?.message || '预约失败'
    ElMessage.error(msg)
  }
}

function handleLaterPay() {
  showPayDialog.value = false
}

function handlePayDialogClose() {
  router.push('/orders')
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
    ElMessage.success('支付成功')
    showPayDialog.value = false
    fetchBookings()
  } catch (e) {
    const msg = e?.response?.data?.message || '支付失败，请检查余额'
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
  max-width: 1180px;
  margin: 0 auto;
  padding: 22px 24px 80px;
}

.detail-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.toolbar-title {
  font-size: var(--fs-12);
  letter-spacing: 0.1em;
  color: var(--ink-4);
}

.detail-loading {
  padding: 26px;
}

/* ---------- 抬头 ---------- */

.venue-head {
  display: grid;
  grid-template-columns: minmax(0, 340px) minmax(0, 1fr);
  gap: 0;
  overflow: hidden;
  margin-bottom: 18px;
}

.head-photo {
  position: relative;
  min-height: 190px;
  background-color: #17281f;
  background-image: radial-gradient(60% 50% at 50% 50%, rgba(232, 163, 61, 0.14), transparent 72%);
}

.head-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: saturate(0.86) contrast(1.06) brightness(0.96);
}

.head-photo-grade,
.side-photo-grade {
  position: absolute;
  inset: 0;
  pointer-events: none;
  mix-blend-mode: multiply;
  background: linear-gradient(180deg, rgba(60, 46, 22, 0.05) 0%, rgba(11, 16, 14, 0.36) 100%);
}

.head-copy {
  padding: 26px 28px;
  min-width: 0;
}

.head-title {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 22px;
}

.head-title h1 {
  font-size: clamp(22px, 2.4vw, 30px);
  font-weight: 800;
  letter-spacing: -0.025em;
  color: var(--ink-1);
  margin: 0;
}

.head-facts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 18px 24px;
}

.head-facts > div {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
}

.fact-label {
  font-size: var(--fs-11);
  font-weight: 700;
  letter-spacing: 0.1em;
  color: var(--ink-4);
}

.fact-value {
  font-size: var(--fs-13);
  color: var(--ink-2);
  overflow-wrap: anywhere;
}

/* ---------- 主区 / 侧栏 ---------- */

.detail-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 18px;
  align-items: start;
}

.board-panel {
  padding: 22px 24px 26px;
  min-width: 0;
}

.board-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
  padding-bottom: 18px;
  border-bottom: 1px solid var(--border-soft);
}

.board-head-left h2 {
  font-size: var(--fs-18);
  font-weight: 800;
  margin: 0;
  color: var(--ink-1);
}

.board-head-left p {
  margin: 6px 0 0;
  font-size: var(--fs-12);
  color: var(--ink-3);
}

.date-picker {
  width: 190px;
}

.board-legend {
  display: flex;
  align-items: center;
  gap: 18px;
  flex-wrap: wrap;
  margin: 16px 0 14px;
  font-size: var(--fs-12);
  color: var(--ink-3);
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 7px;
}

.dot {
  width: 9px;
  height: 9px;
  border-radius: 3px;
  display: inline-block;
}

.dot--free {
  background: var(--surface-2);
  border: 1px solid var(--border-strong);
}

.dot--booked {
  background: var(--sunken);
  border: 1px solid var(--border);
}

.dot--member {
  background: var(--accent-soft);
  border: 1px solid var(--accent-line);
}

.legend-member {
  color: var(--accent);
  font-weight: 600;
}

/* ---------- 棋盘 ---------- */

.board {
  display: grid;
  grid-template-columns: 96px repeat(var(--cols), minmax(0, 1fr));
  gap: 5px;
  min-width: 0;
}

.board-corner,
.board-court {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 34px;
  font-size: var(--fs-11);
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--ink-4);
}

.board-court {
  color: var(--ink-2);
  font-size: var(--fs-12);
  border-radius: 8px;
  background: var(--sunken);
}

.board-time {
  display: flex;
  align-items: center;
  font-size: var(--fs-12);
  color: var(--ink-3);
  white-space: nowrap;
}

.cell {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: var(--tap);
  padding: 0 4px;
  border: 1px solid var(--border);
  border-radius: 9px;
  background: var(--surface);
  color: var(--ink-1);
  cursor: pointer;
  transition: background-color var(--dur-2) var(--ease-out),
    border-color var(--dur-2) var(--ease-out), transform var(--dur-1) var(--ease-out);
}

.cell-price {
  font-size: var(--fs-12);
  font-weight: 700;
  color: var(--accent);
}

.cell.is-booked {
  background: var(--sunken);
  border-color: var(--border-soft);
  cursor: not-allowed;
}

.cell-state {
  font-size: var(--fs-11);
  font-weight: 600;
  color: var(--ink-4);
}

@media (hover: hover) and (pointer: fine) {
  .cell:not(.is-booked):hover {
    background: var(--accent-soft);
    border-color: var(--accent);
    transform: translateY(-1px);
  }
}

.cell:not(.is-booked):active {
  transform: translateY(0);
}

/* 手机版棋盘 */
.board-list {
  display: none;
}

.board-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 54px 20px;
  text-align: center;
  color: var(--ink-3);
}

.board-placeholder strong {
  font-size: var(--fs-14);
  color: var(--ink-2);
}

.board-placeholder span {
  font-size: var(--fs-12);
  max-width: 36ch;
  line-height: var(--lh-body);
}

/* ---------- 侧栏 ---------- */

.detail-side {
  display: flex;
  flex-direction: column;
  gap: 18px;
  min-width: 0;
}

.side-photo {
  position: relative;
  aspect-ratio: 4 / 3;
  overflow: hidden;
  background-color: #17281f;
}

.side-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: saturate(0.86) contrast(1.06) brightness(0.96);
}

.receipt {
  padding: 18px 20px 20px;
}

.receipt-title {
  margin: 0 0 14px;
  font-size: var(--fs-14);
  font-weight: 800;
  color: var(--accent);
  letter-spacing: 0.02em;
}

.receipt-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  padding: 7px 0;
  font-size: var(--fs-13);
  color: var(--ink-3);
}

.receipt-row strong {
  color: var(--ink-1);
  font-weight: 700;
}

.receipt-note {
  margin: 12px 0 0;
  font-size: var(--fs-12);
  line-height: var(--lh-body);
  color: var(--ink-3);
}

/* ---------- 支付弹窗 ---------- */

.pay-summary {
  padding: 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--sunken);
}

.pay-summary-head {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 14px;
  margin-bottom: 8px;
  border-bottom: 1px solid var(--border-soft);
}

.pay-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  flex: 0 0 38px;
  border-radius: 11px;
  color: var(--accent);
  background: var(--accent-soft);
}

.pay-summary-head strong {
  display: block;
  font-size: var(--fs-14);
  font-weight: 700;
  color: var(--ink-1);
}

.pay-summary-head span {
  font-size: var(--fs-12);
  color: var(--ink-3);
}

.pay-detail-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  padding: 6px 0;
  font-size: var(--fs-13);
  color: var(--ink-3);
}

.pay-detail-row strong {
  color: var(--ink-1);
}

.original-price {
  color: var(--ink-4);
  text-decoration: line-through;
}

.discount-row strong {
  color: var(--accent);
}

.amount-row {
  padding-top: 12px;
  margin-top: 8px;
  border-top: 1px solid var(--border-soft);
}

.amount-row strong {
  font-size: var(--fs-22);
  font-weight: 800;
  color: var(--accent);
}

.pay-methods-title {
  margin: 20px 0 12px;
  font-size: var(--fs-13);
  font-weight: 700;
  color: var(--ink-2);
}

.pay-methods {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.pay-methods :deep(.el-radio) {
  width: 100%;
  margin-right: 0;
  height: 44px;
}

/* ---------- 断点 ---------- */

@media (max-width: 1080px) {
  .detail-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .detail-side {
    flex-direction: row;
  }

  .detail-side > * {
    flex: 1;
  }

  .side-photo {
    aspect-ratio: 16 / 9;
  }
}

@media (max-width: 860px) {
  .venue-head {
    grid-template-columns: minmax(0, 1fr);
  }

  .head-photo {
    min-height: 170px;
    aspect-ratio: 21 / 9;
  }

  /* 桌面的棋盘在小屏上换成一行一个时段 */
  .board {
    display: none;
  }

  .board-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .slot-row {
    display: grid;
    grid-template-columns: 92px minmax(0, 1fr);
    align-items: start;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid var(--border-soft);
  }

  .slot-row:last-child {
    border-bottom: 0;
  }

  .slot-time {
    font-size: var(--fs-12);
    color: var(--ink-3);
    padding-top: 10px;
  }

  .slot-courts {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    min-width: 0;
  }

  .court-chip {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    min-height: 40px;
    padding: 0 12px;
    border: 1px solid var(--border);
    border-radius: 999px;
    background: var(--surface);
    cursor: pointer;
    transition: border-color var(--dur-2) var(--ease-out), background-color var(--dur-2) var(--ease-out);
  }

  .court-chip .chip-name {
    font-size: var(--fs-12);
    font-weight: 600;
    color: var(--ink-2);
  }

  .court-chip .chip-price {
    font-size: var(--fs-12);
    font-weight: 700;
    color: var(--accent);
  }

  .court-chip.is-booked {
    background: var(--sunken);
    border-color: var(--border-soft);
    cursor: not-allowed;
  }

  .court-chip.is-booked .chip-name,
  .court-chip.is-booked .chip-price {
    color: var(--ink-4);
  }
}

@media (max-width: 640px) {
  .venue-detail {
    padding: 16px 14px 64px;
  }

  .board-panel {
    padding: 18px 16px 20px;
  }

  .date-picker {
    width: 100%;
  }

  .detail-side {
    flex-direction: column;
  }

  .head-copy {
    padding: 20px 18px 22px;
  }
}
</style>
