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
            alt="室内球场地面与场地线"
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
          <div v-if="!venue.is_active" class="venue-closed">
            <el-icon :size="18"><WarningFilled /></el-icon>
            <span>该场馆已停用，仅可查看场地与时段，暂不支持预约。</span>
          </div>
          <header class="board-head">
            <div class="board-head-left">
              <h2>选时段</h2>
              <p>先选日期，再点棋盘上任意一格</p>
            </div>
            <div class="board-head-right">
              <div class="date-quick">
                <button
                  type="button"
                  class="quick-chip"
                  :class="{ 'is-on': bookDate === quickToday, 'is-full': isDayFull(quickToday) }"
                  :disabled="isDayFull(quickToday)"
                  :title="isDayFull(quickToday) ? '今天已无可约时段' : '查看今天的可约时段'"
                  @click="jumpDate(0)"
                >
                  今天<small v-if="isDayFull(quickToday)">已满</small>
                </button>
                <button
                  type="button"
                  class="quick-chip"
                  :class="{ 'is-on': bookDate === quickTomorrow, 'is-full': isDayFull(quickTomorrow) }"
                  :disabled="isDayFull(quickTomorrow)"
                  :title="isDayFull(quickTomorrow) ? '明天已无可约时段' : '查看明天的可约时段'"
                  @click="jumpDate(1)"
                >
                  明天<small v-if="isDayFull(quickTomorrow)">已满</small>
                </button>
              </div>
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
              <span v-if="bookDate === quickToday" class="legend-item">
                <i class="dot dot--past"></i>已过时段
              </span>
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
              <div class="board" :key="bookDate" :style="boardStyle" v-loading="bookingLoading">
                <div class="board-corner mono">时段 \ 场地</div>
                <div v-for="c in courts" :key="'h' + c.id" class="board-court">{{ c.name }}</div>

                <template v-for="(s, row) in slots" :key="s.id">
                  <div class="board-time mono drop-in" :style="{ '--i': row }">{{ s.display }}</div>
                  <button
                    v-for="c in courts"
                    :key="c.id + '-' + s.id"
                    type="button"
                    class="cell drop-in"
                    :style="{ '--i': row }"
                    :class="{ 'is-booked': isBooked(c, s), 'is-past': isPastSlot(s), 'is-off': !venue.is_active }"
                    :disabled="isBooked(c, s) || isPastSlot(s) || !venue.is_active"
                    :aria-label="`${c.name} ${s.display} ${isBooked(c, s) ? '已预约' : isPastSlot(s) ? '已过时段' : '可预约'}`"
                    @click="pick(c, s)"
                  >
                    <span v-if="isBooked(c, s)" class="cell-state">已订</span>
                    <span v-else-if="isPastSlot(s)" class="cell-state">已过</span>
                    <span v-else class="cell-price mono">¥{{ memberPrice(s) }}</span>
                  </button>
                </template>
              </div>

              <!-- 手机：一个时段一行，可约的场地做成小块 -->
              <div class="board-list" :key="bookDate + '-m'" v-loading="bookingLoading">
                <div v-for="(s, row) in slots" :key="'m' + s.id" class="slot-row">
                  <div class="slot-time mono drop-in" :style="{ '--i': row }">{{ s.display }}</div>
                  <div class="slot-courts">
                    <button
                      v-for="c in courts"
                      :key="'m' + c.id + '-' + s.id"
                      type="button"
                      class="court-chip"
                      :class="{ 'is-booked': isBooked(c, s), 'is-past': isPastSlot(s), 'is-off': !venue.is_active }"
                      :disabled="isBooked(c, s) || isPastSlot(s) || !venue.is_active"
                      :aria-label="`${c.name} ${s.display} ${isBooked(c, s) ? '已预约' : isPastSlot(s) ? '已过时段' : '可预约'}`"
                      @click="pick(c, s)"
                    >
                      <span class="chip-name">{{ c.name }}</span>
                      <span class="chip-price mono">{{ isBooked(c, s) ? '已订' : isPastSlot(s) ? '已过' : '¥' + memberPrice(s) }}</span>
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
              src="/img/venue-detail-net.jpg"
              alt="球馆看台与木地板"
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
              <strong class="mono">¥{{ balance.toFixed(2) }}</strong>
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
        <el-radio value="balance" border :disabled="balance < payForm.amount">
          余额支付 (¥<span class="mono">{{ balance.toFixed(2) }}</span>)
          <span v-if="balance < payForm.amount" class="pay-hint">· 余额不足</span>
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
import { computed, ref, onMounted, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Back, OfficeBuilding, Calendar, Wallet, WarningFilled } from '@element-plus/icons-vue'
import { venueApi } from '@/api/venues'
import { bookingApi } from '@/api/bookings'
import { paymentApi } from '@/api/payments'
import { couponApi } from '@/api/coupons'
import { useUserStore } from '@/store'
import { hideBrokenImage } from '@/utils/venueVisual'
import { discountText } from '@/utils/format'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const venue = ref(null)
const loading = ref(true)
const bookingLoading = ref(false)
const stayAfterPay = ref(false)
const bookDate = ref('')
const selectedCourt = ref(null)
const bookedSlots = ref([])
const bookedDate = ref('')
/** 各日期剩余的「可约格子」数：{ 'YYYY-MM-DD': n }，只在预取过的日期上有值 */
const dayRemaining = ref({})
const showPayDialog = ref(false)
const paying = ref(false)
const coupons = ref([])
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
const balance = computed(() => Number(userStore.userInfo?.balance || 0) || 0)
const quickToday = computed(() => formatDate(0))
const quickTomorrow = computed(() => formatDate(1))

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

function disabledDate(time) {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  if (time.getTime() < today.getTime()) return true
  // 已约满的日期同样不许选（只对预取过的 7 天有效，其余照常可选）
  const key = `${time.getFullYear()}-${pad(time.getMonth() + 1)}-${pad(time.getDate())}`
  return dayRemaining.value[key] === 0
}

function pad(n) {
  return String(n).padStart(2, '0')
}

function formatDate(offset = 0) {
  const d = new Date()
  d.setDate(d.getDate() + offset)
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${m}-${day}`
}

/** 快捷跳转：今天 / 明天（点当前已选日期也重新拉一次占用） */
function jumpDate(offset) {
  bookDate.value = formatDate(offset)
  fetchBookings()
}

/** 某片场地某个时段是否已经被占 */
function isBooked(court, slot) {
  const courtId = court?.id
  if (!courtId) return false
  return bookedSlots.value.some((o) => o.court_id === courtId && o.time_slot_id === slot.id)
}

/** 这个时段的开场时间是不是已经过去了（只对「今天」有意义） */
function slotStarted(slot) {
  const matched = String(slot?.start_time || '').match(/^(\d{1,2}):(\d{2})/)
  if (!matched) return false
  const now = new Date()
  const start = new Date(
    now.getFullYear(), now.getMonth(), now.getDate(),
    Number(matched[1]), Number(matched[2]), 0, 0,
  )
  return now.getTime() >= start.getTime()
}

/** 今天已开场的时段不可选：19:23 时，19:00-20:00 及更早的时段全部禁用 */
function isPastSlot(slot) {
  if (bookDate.value !== formatDate(0)) return false
  return slotStarted(slot)
}

/** 这一天是不是一个可约格子都不剩（今天还要扣掉已开场的时段） */
function isDayFull(dateStr) {
  return dayRemaining.value[dateStr] === 0
}

/** 预取未来 7 天占用，算出每天的剩余可约格数，用来把日期按钮标灰 */
async function fetchDayRemaining() {
  const venueId = venue.value?.id
  const cells = courts.value.length * slots.value.length
  if (!venueId || !cells) return
  const dates = Array.from({ length: 7 }, (_, i) => formatDate(i))
  const results = await Promise.allSettled(
    dates.map((date) => venueApi.availability(venueId, { date })),
  )
  const next = {}
  results.forEach((res, i) => {
    if (res.status !== 'fulfilled') return
    const date = dates[i]
    const occupied = (res.value?.occupied || []).length
    const past = date === formatDate(0) ? slots.value.filter(slotStarted).length * courts.value.length : 0
    next[date] = Math.max(cells - occupied - past, 0)
  })
  dayRemaining.value = next
  return next
}

/** 'YYYY-MM-DD' → '10月22日'，提示文案用 */
function humanDate(dateStr) {
  const parts = String(dateStr).split('-')
  if (parts.length !== 3) return dateStr
  return `${Number(parts[1])}月${Number(parts[2])}日`
}

/** 从今天起找最近一个还有空位的日期：已预取的 7 天直接查表，之后按天往后问，最多找 30 天 */
async function findNextAvailableDay(known = {}) {
  const venueId = venue.value?.id
  if (!venueId) return ''
  const cells = courts.value.length * slots.value.length
  for (let i = 0; i < 30; i += 1) {
    const key = formatDate(i)
    if (Object.prototype.hasOwnProperty.call(known, key)) {
      if (known[key] > 0) return key
      continue
    }
    try {
      const res = await venueApi.availability(venueId, { date: key })
      if (cells - (res?.occupied || []).length > 0) return key
    } catch {
      // 单日请求失败就当这天没空位，继续往后找
    }
  }
  return ''
}

/** 今天约满时自动跳到最近一个还有空位的日期，省得用户自己去翻日历 */
async function autoJumpToAvailableDay() {
  const map = await fetchDayRemaining()
  if (!isDayFull(formatDate(0))) return
  const target = await findNextAvailableDay(map)
  if (!target) {
    ElMessage.warning('最近 30 天都没有可约时段了，换个场馆或稍后再看')
    return
  }
  bookDate.value = target
  fetchBookings()
  ElMessage.info(`今天已约满，已自动切换到 ${humanDate(target)}`)
}

/** 棋盘上点一格：等价于「选中这片场地 + 预约这个时段」 */
function pick(court, slot) {
  if (!venue.value?.is_active) {
    ElMessage.warning('该场馆已停用，暂不可预约')
    return
  }
  if (isBooked(court, slot)) return
  if (isPastSlot(slot)) {
    ElMessage.warning('该时段已开场，请选择更晚的时段')
    return
  }
  selectedCourt.value = court
  handleBook(slot)
}

async function fetchVenue() {
  try {
    const res = await venueApi.detail(route.params.id)
    venue.value = res
    // 默认选中今天并拉取占用，省掉一步"先选日期"
    bookDate.value = formatDate(0)
    fetchBookings()
    fetchCoupons()
    // 今天约满就直接落到最近一个有空位的日期
    await autoJumpToAvailableDay()
  } catch {
    ElMessage.error('获取场馆信息失败')
  } finally {
    loading.value = false
  }
}

async function fetchCoupons() {
  try {
    const res = await couponApi.my({ status: 'unused' })
    const now = new Date()
    coupons.value = (res.data || []).filter((u) => new Date(u.expires_at) > now)
  } catch {
    coupons.value = []
  }
}

/** 下单自动使用最优可用券（面额最大且满足满减）；券页可查我的券 */
function bestCoupon(price) {
  return coupons.value
    .filter((u) => Number(u.min_amount) <= Number(price))
    .sort((a, b) => Number(b.amount) - Number(a.amount))[0] || null
}

async function fetchBookings() {
  if (!bookDate.value || !venue.value) return
  bookingLoading.value = true
  try {
    const res = await venueApi.availability(venue.value.id, { date: bookDate.value })
    bookedSlots.value = res.occupied || []
    bookedDate.value = bookDate.value
  } catch {
    // 刷新失败保留旧数据（避免棋盘突然全绿误导下单）；
    // 只有旧数据不属于当前日期时才清空，防止跨日期污染
    if (bookedDate.value !== bookDate.value) bookedSlots.value = []
    ElMessage.warning('占用状态刷新失败，请稍后重试')
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
    const coupon = bestCoupon(memberPrice(slot))
    const rows = [
      h('div', { class: 'book-confirm-row' }, [
        h('span', '场地'),
        h('strong', `${venue.value.name} · ${selectedCourt.value.name}`),
      ]),
      h('div', { class: 'book-confirm-row' }, [h('span', '日期'), h('strong', { class: 'mono' }, date)]),
      h('div', { class: 'book-confirm-row' }, [h('span', '时段'), h('strong', { class: 'mono' }, slot.display)]),
    ]
    if (coupon) {
      rows.push(h('div', { class: 'book-confirm-row' }, [
        h('span', '优惠券'),
        h('strong', { class: 'mono accent' }, `-¥${Number(coupon.amount).toFixed(2)}（自动使用最优券）`),
      ]))
    }
    rows.push(h('div', { class: 'book-confirm-row book-confirm-amount' }, [
      h('span', '金额'),
      h('strong', { class: 'mono' }, `¥${memberPrice(slot)}${coupon ? '（以订单实付为准）' : ''}`),
    ]))
    await ElMessageBox({
      title: '预约确认',
      message: h('div', { class: 'book-confirm' }, rows),
      confirmButtonText: '确认下单',
      cancelButtonText: '取消',
      type: 'info',
    })
  } catch {
    return
  }
  try {
    const payload = {
      court: courtId,
      date: date,
      time_slot: slot.id,
    }
    const coupon = bestCoupon(memberPrice(slot))
    if (coupon) payload.user_coupon_id = coupon.id
    const booking = await bookingApi.create(payload)
    stayAfterPay.value = false
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
    fetchDayRemaining()
  } catch (e) {
    const msg = e?.response?.data?.[0] || e?.response?.data?.message || '预约失败'
    ElMessage.error(msg)
  }
}

function handleLaterPay() {
  stayAfterPay.value = false
  showPayDialog.value = false
}

function handlePayDialogClose() {
  // 支付成功后留在本页看棋盘刷新；"稍后支付"/右上角关闭才去订单页
  if (!stayAfterPay.value) router.push('/orders')
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
    stayAfterPay.value = true
    showPayDialog.value = false
    fetchBookings()
    fetchDayRemaining()
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
  padding: var(--sp-6) var(--sp-6) var(--sp-12);
}

.detail-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--sp-4);
  margin-bottom: var(--sp-5);
}

.toolbar-title {
  font-size: var(--fs-12);
  letter-spacing: var(--track-caps);
  color: var(--ink-4);
}

.detail-loading {
  padding: var(--sp-7);
}

/* ---------- 抬头 ---------- */

.venue-head {
  display: grid;
  grid-template-columns: minmax(0, 340px) minmax(0, 1fr);
  gap: 0;
  overflow: hidden;
  margin-bottom: var(--sp-5);
}

.head-photo {
  position: relative;
  min-height: 190px;
  background-color: var(--sunken);
  background-image: radial-gradient(60% 50% at 50% 50%, var(--accent-soft), transparent 72%);
}

.head-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: saturate(0.92) contrast(1.05) brightness(1.02);
}

.head-photo-grade,
.side-photo-grade {
  position: absolute;
  inset: 0;
  pointer-events: none;
  mix-blend-mode: multiply;
  background: linear-gradient(180deg, transparent 0%, color-mix(in srgb, var(--ink-1) 26%, transparent) 100%);
}

.head-copy {
  padding: var(--sp-7) var(--sp-7);
  min-width: 0;
}

.head-title {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
  flex-wrap: wrap;
  margin-bottom: var(--sp-6);
}

.head-title h1 {
  font-size: clamp(22px, 2.4vw, 30px);
  font-weight: 800;
  letter-spacing: var(--track-display);
  color: var(--ink-1);
  margin: 0;
}

.head-facts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: var(--sp-5) var(--sp-6);
}

.head-facts > div {
  display: flex;
  flex-direction: column;
  gap: var(--sp-1);
  min-width: 0;
}

.fact-label {
  font-size: var(--fs-11);
  font-weight: 700;
  letter-spacing: var(--track-caps);
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
  gap: var(--sp-5);
  align-items: start;
}

.board-panel {
  padding: var(--sp-6) var(--sp-6) var(--sp-7);
  min-width: 0;
}

.board-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--sp-5);
  flex-wrap: wrap;
  padding-bottom: var(--sp-5);
  border-bottom: 1px solid var(--border-soft);
}

.board-head-left h2 {
  font-size: var(--fs-18);
  font-weight: 800;
  margin: 0;
  color: var(--ink-1);
}

.board-head-left p {
  margin: var(--sp-2) 0 0;
  font-size: var(--fs-12);
  color: var(--ink-3);
}

.date-picker {
  width: 190px;
}

.board-head-right {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
}

.date-quick {
  display: flex;
  gap: var(--sp-2);
}

.quick-chip {
  padding: var(--sp-2) var(--sp-4);
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--surface);
  color: var(--ink-2);
  font-size: var(--fs-12);
  font-weight: 600;
  cursor: pointer;
  transition: border-color var(--dur-2) var(--ease-out), color var(--dur-2) var(--ease-out),
    background-color var(--dur-2) var(--ease-out), transform var(--dur-1) var(--ease-spring);
}

.quick-chip:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.quick-chip:active {
  transform: scale(0.96);
}

.quick-chip.is-on {
  background: var(--accent-soft);
  border-color: var(--accent-line);
  color: var(--accent);
}

.quick-chip small {
  margin-left: 4px;
  font-size: 10px;
  font-weight: 600;
  color: var(--ink-4);
}

/* 当天一个可约格子都不剩：虚线灰底，点不动 */
.quick-chip.is-full,
.quick-chip.is-full:hover {
  background: var(--sunken);
  border-style: dashed;
  border-color: var(--border-soft);
  color: var(--ink-4);
  cursor: not-allowed;
}

.quick-chip:disabled {
  cursor: not-allowed;
}

.quick-chip:disabled:active {
  transform: none;
}

.board-legend {
  display: flex;
  align-items: center;
  gap: var(--sp-5);
  flex-wrap: wrap;
  margin: var(--sp-4) 0 var(--sp-4);
  font-size: var(--fs-12);
  color: var(--ink-3);
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: var(--sp-2);
}

.dot {
  width: 9px;
  height: 9px;
  border-radius: var(--radius-xs);
  display: inline-block;
}

.dot--free {
  background: var(--surface);
  border: 1px solid var(--border);
}

.dot--booked {
  background: var(--sunken);
  border: 1px solid var(--border-soft);
}

.dot--past {
  background: var(--sunken);
  border: 1px dashed var(--border-strong);
}

.dot--member {
  background: var(--accent-soft);
  border: 1px solid var(--accent-line);
}

.legend-member {
  color: var(--accent);
  font-weight: 600;
}

/* ---------- 停用提示 ---------- */

.venue-closed {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  margin-bottom: var(--sp-4);
  padding: var(--sp-3) var(--sp-4);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--warn-soft);
  color: var(--warn);
  font-size: var(--fs-13);
  font-weight: 600;
}

/* ---------- 棋盘 ---------- */

.board {
  display: grid;
  grid-template-columns: 96px repeat(var(--cols), minmax(0, 1fr));
  gap: var(--gap-grid);
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
  border-radius: var(--radius-sm);
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
  padding: 0 var(--sp-1);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface);
  color: var(--ink-1);
  cursor: pointer;
  transition: background-color var(--dur-2) var(--ease-out),
    border-color var(--dur-2) var(--ease-out), transform var(--dur-1) var(--ease-spring);
}

.cell-price {
  font-size: var(--fs-12);
  font-weight: 700;
  color: var(--ink-1);
}

/* 主色只标"可点"：悬停或键盘聚焦时才点亮 */
.cell:not(.is-booked):not(.is-off):not(.is-past):hover .cell-price,
.cell:not(.is-booked):not(.is-off):not(.is-past):focus-visible .cell-price {
  color: var(--accent);
}

.cell.is-booked {
  background: var(--sunken);
  border-color: var(--border-soft);
  cursor: not-allowed;
}

/* 今天已开场的时段：虚线灰格，只提示不可点 */
.cell.is-past {
  background: var(--sunken);
  border-style: dashed;
  border-color: var(--border-soft);
  cursor: not-allowed;
}

/* 场馆停用：格子可见但不可点 */
.cell.is-off {
  cursor: not-allowed;
}

.cell.is-off .cell-price {
  color: var(--ink-4);
}

.cell-state {
  font-size: var(--fs-11);
  font-weight: 600;
  color: var(--ink-4);
}

@media (hover: hover) and (pointer: fine) {
  .cell:not(.is-booked):not(.is-off):not(.is-past):hover {
    background: var(--accent-soft);
    border-color: var(--accent);
    transform: translateY(-1px);
  }
}

/* 弹簧按压反馈（第 5 拍）：按下缩一格、松开弹回 */
.cell:not(.is-booked):not(.is-off):not(.is-past):active {
  transform: scale(0.96);
  background: var(--accent-soft);
  border-color: var(--accent);
}

/* 手机版棋盘 */
.board-list {
  display: none;
}

.board-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--sp-3);
  padding: var(--sp-10) var(--sp-5);
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
  gap: var(--sp-5);
  min-width: 0;
}

.side-photo {
  position: relative;
  aspect-ratio: 3 / 2;
  overflow: hidden;
  background-color: var(--sunken);
}

.side-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: saturate(0.92) contrast(1.05) brightness(1.02);
}

.receipt {
  padding: var(--sp-5);
}

.receipt-title {
  margin: 0 0 var(--sp-4);
  font-size: var(--fs-14);
  font-weight: 800;
  color: var(--accent);
  letter-spacing: 0.02em;
}

.receipt-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--sp-3);
  padding: var(--sp-2) 0;
  font-size: var(--fs-13);
  color: var(--ink-3);
}

.receipt-row strong {
  color: var(--ink-1);
  font-weight: 700;
}

.receipt-note {
  margin: var(--sp-3) 0 0;
  font-size: var(--fs-12);
  line-height: var(--lh-body);
  color: var(--ink-3);
}

/* ---------- 支付弹窗 ---------- */

.pay-summary {
  padding: var(--sp-4);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--sunken);
}

.pay-summary-head {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
  padding-bottom: var(--sp-4);
  margin-bottom: var(--sp-2);
  border-bottom: 1px solid var(--border-soft);
}

.pay-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  flex: 0 0 38px;
  border-radius: var(--radius);
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
  gap: var(--sp-3);
  padding: var(--sp-2) 0;
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
  padding-top: var(--sp-3);
  margin-top: var(--sp-2);
  border-top: 1px solid var(--border-soft);
}

.amount-row strong {
  font-size: var(--fs-22);
  font-weight: 800;
  color: var(--accent);
}

.pay-methods-title {
  margin: var(--sp-5) 0 var(--sp-3);
  font-size: var(--fs-13);
  font-weight: 700;
  color: var(--ink-2);
}

.pay-methods {
  display: flex;
  flex-direction: column;
  gap: var(--sp-3);
  width: 100%;
}

.pay-methods :deep(.el-radio) {
  width: 100%;
  margin-right: 0;
  height: var(--tap);
}

.pay-hint {
  font-size: var(--fs-12);
  color: var(--ink-4);
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
    gap: var(--sp-3);
  }

  .slot-row {
    display: grid;
    grid-template-columns: 92px minmax(0, 1fr);
    align-items: start;
    gap: var(--sp-3);
    padding: var(--sp-3) 0;
    border-bottom: 1px solid var(--border-soft);
  }

  .slot-row:last-child {
    border-bottom: 0;
  }

  .slot-time {
    font-size: var(--fs-12);
    color: var(--ink-3);
    padding-top: var(--sp-3);
  }

  .slot-courts {
    display: flex;
    flex-wrap: wrap;
    gap: var(--sp-2);
    min-width: 0;
  }

  .court-chip {
    display: inline-flex;
    align-items: center;
    gap: var(--sp-2);
    min-height: var(--tap);
    padding: 0 var(--sp-3);
    border: 1px solid var(--border);
    border-radius: 999px;
    background: var(--surface);
    cursor: pointer;
    transition: border-color var(--dur-2) var(--ease-out), background-color var(--dur-2) var(--ease-out),
      transform var(--dur-1) var(--ease-spring);
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

  /* 今天已开场的时段：虚线灰块 */
  .court-chip.is-past {
    background: var(--sunken);
    border-style: dashed;
    border-color: var(--border-soft);
    cursor: not-allowed;
  }

  .court-chip.is-booked .chip-name,
  .court-chip.is-booked .chip-price {
    color: var(--ink-4);
  }

  .court-chip.is-off {
    cursor: not-allowed;
  }

  .court-chip.is-off .chip-name,
  .court-chip.is-off .chip-price {
    color: var(--ink-4);
  }

  /* 弹簧按压反馈（第 5 拍）：触屏按下的即时反馈 */
  .court-chip:not(.is-booked):not(.is-off):not(.is-past):active {
    transform: scale(0.96);
  }
}

@media (max-width: 640px) {
  .venue-detail {
    padding: var(--sp-4) var(--sp-4) var(--sp-11);
  }

  .board-panel {
    padding: var(--sp-5) var(--sp-4) var(--sp-5);
  }

  .date-picker {
    width: 100%;
  }

  .board-head-right {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }

  .date-quick {
    width: 100%;
  }

  .quick-chip {
    flex: 1;
  }

  .detail-side {
    flex-direction: column;
  }

  .head-copy {
    padding: var(--sp-5) var(--sp-5) var(--sp-6);
  }
}
</style>
<style>
/* 预约确认弹窗的内容区：ElMessageBox 把内容渲染进 body（teleport），
   scoped 样式管不到它，这里用一层全局样式，全部走设计令牌。 */
.book-confirm {
  display: flex;
  flex-direction: column;
  gap: var(--sp-2);
  min-width: 240px;
  font-size: var(--fs-13);
}

.book-confirm-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--sp-4);
}

.book-confirm-row span {
  color: var(--ink-3);
}

.book-confirm-row strong {
  color: var(--ink-1);
  font-weight: 700;
  text-align: right;
}

.book-confirm-amount strong {
  font-size: var(--fs-16);
  color: var(--accent);
}
</style>
