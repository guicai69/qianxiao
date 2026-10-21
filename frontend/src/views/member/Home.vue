<template>
  <div class="member-home">
    <!-- 首屏：走进球馆 -->
    <section class="hero" >
      <CourtScene />

      <div class="hero-inner">
        <p class="hero-kicker mono fx-rise" style="--i: 0">广州 · {{ totalVenues }} 座球馆 · {{ totalCourts }} 片场地</p>

        <h1 class="display-1 hero-title">
          <span class="split" aria-hidden="true">
            <i
              v-for="(ch, i) in titleA"
              :key="'a' + i"
              class="ch"
              :style="{ '--i': i }"
            >{{ ch }}</i>
          </span>
          <span class="sr-only">把今晚的场，</span>
          <br />
          <span class="split" aria-hidden="true">
            <i
              v-for="(ch, i) in titleB"
              :key="'b' + i"
              class="ch"
              :style="{ '--i': i + titleA.length }"
            >{{ ch }}</i>
          </span>
          <span class="sr-only">提前订下来。</span>
        </h1>

        <p class="lede hero-lede fx-rise" style="--i: 6">
          场馆、场地、时段一处看清。会员折扣自动算进价格，到店前台签到即核销。
        </p>

        <div class="hero-actions fx-rise" style="--i: 7">
          <el-button type="primary" size="large" class="hero-cta fx-press" @click="startBooking">
            开始预约
            <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>
          <button v-if="userStore.isLoggedIn" class="link-ghost" @click="router.push('/orders')">
            查看我的订单
          </button>
          <button v-else class="link-ghost" @click="router.push('/register')">
            还没有账号？注册
          </button>
        </div>

        <ol class="steps mono fx-rise" style="--i: 8">
          <li>选场馆</li>
          <li>挑时段</li>
          <li>到店核销</li>
        </ol>
      </div>
    </section>

    <!-- 规格带：真数字，不是"高效便捷"那种形容词 -->
    <section class="band-section">
      <div class="spec-band reveal">
        <div class="spec">
          <div class="spec__num roll" style="--i: 0"><span>{{ pad(totalVenues) }}</span></div>
          <div class="spec__label">座球馆</div>
        </div>
        <div class="spec">
          <div class="spec__num roll" style="--i: 1"><span>{{ totalCourts }}</span></div>
          <div class="spec__label">片场地</div>
        </div>
        <div class="spec">
          <div class="spec__num roll" style="--i: 2"><span>14</span></div>
          <div class="spec__label">个时段 / 天</div>
        </div>
        <div class="spec">
          <div class="spec__num roll" style="--i: 3"><span>¥30<small>起</small></span></div>
          <div class="spec__label">每小时</div>
        </div>
      </div>
    </section>

    <!-- 名单跑马灯：五座球馆横向缓慢流转，纯装饰（数据仍来自真实场馆） -->
    <section v-if="sheet.length" class="ticker-section">
      <div class="fx-marquee ticker" aria-hidden="true">
        <div class="fx-marquee__track">
          <span v-for="v in sheet" :key="'t1-' + v.id" class="ticker__item mono">
            <b>{{ v.no }}</b>
            <span>{{ v.name }}</span>
            <em>{{ districtOf(v) }}区</em>
          </span>
          <span v-for="v in sheet" :key="'t2-' + v.id" class="ticker__item mono">
            <b>{{ v.no }}</b>
            <span>{{ v.name }}</span>
            <em>{{ districtOf(v) }}区</em>
          </span>
        </div>
      </div>
    </section>

    <!-- 印相表：一排球场就是一张接触印相表，逐格挑选 -->
    <section class="sheet-section">
      <header class="section-head">
        <div>
          <h2 class="display-3">场馆印相表</h2>
          <p class="section-sub">一格一座球馆，点开挑场地与时段</p>
        </div>
        <span class="section-count mono">{{ sheet.length ? sheet.length + ' 家' : '待登录' }}</span>
      </header>

      <div v-if="sheet.length" class="sheet">
        <button
          v-for="v in sheet"
          :key="v.id"
          type="button"
          class="frame frame--link reveal-stagger fx-sheen fx-hover-parent"
          :style="{ '--i': Number(v.no) - 1 }"
          @click="openVenue(v)"
        >
          <div class="frame__media">
            <img :src="coverUrl(v)" :alt="`${v.name}室内球场`" loading="lazy" decoding="async" @error="hideBrokenImage" />
            <span class="frame__grade"></span>
            <span class="frame__no">{{ v.no }}</span>
          </div>
          <div class="frame__body">
            <h3 class="frame__title">{{ v.name }}</h3>
            <div class="frame__meta">
              <span>{{ districtOf(v) }}区</span>
              <span>{{ v.court_count }} 片场地</span>
            </div>
            <div class="frame__row">
              <span class="frame__addr">{{ v.address || '地址待补充' }}</span>
              <span class="frame__go fx-nudge">
                {{ userStore.isLoggedIn ? '选时段' : '登录后选时段' }}
                <el-icon><ArrowRight /></el-icon>
              </span>
            </div>
          </div>
        </button>
      </div>

      <div v-else class="sheet-locked">
        <div class="locked-copy">
          <h3 class="display-3">印相表要登录才展开</h3>
          <p class="section-sub">
            登录后这里是五座球馆的格子：每格写着场地数量、地址与可预约时段，点进去就能下单。
          </p>
        </div>
        <div class="locked-actions">
          <el-button type="primary" size="large" @click="router.push('/login')">登录</el-button>
          <el-button size="large" @click="router.push('/register')">注册</el-button>
        </div>
      </div>
    </section>

    <!-- 告示条：印相表底下的说明栏 -->
    <section v-if="announcements.length" class="bulletin-section">
      <header class="section-head">
        <div>
          <h2 class="display-3">场馆公告</h2>
          <p class="section-sub">充值赠送、开放时间与临时调整</p>
        </div>
      </header>

      <div class="bulletin reveal">
        <article v-for="a in announcements" :key="a.id" class="bulletin__item">
          <div class="bulletin__body">
            <strong>
              {{ a.title }}
              <el-tag v-if="a.is_pinned" size="small" type="warning" effect="light">置顶</el-tag>
            </strong>
            <p>{{ a.content }}</p>
          </div>
          <time class="bulletin__date">{{ shortDate(a.created_at) }}</time>
        </article>
      </div>
    </section>

    <!-- 收尾：换幕，回到球馆的暗色调 -->
    <section class="closing" data-plane="deep">
      <div class="fx-aurora" aria-hidden="true">
        <span class="fx-aurora__blob"></span>
        <span class="fx-aurora__blob fx-aurora__blob--b"></span>
        <span class="fx-aurora__blob fx-aurora__blob--c"></span>
      </div>
      <div class="closing-inner">
        <h2 class="display-2 drop-in" style="--i: 0">
          {{ userStore.isLoggedIn ? '去挑一块场地' : '注册之后，立刻能订' }}
        </h2>
        <p class="lede closing-lede drop-in" style="--i: 1">
          {{
            userStore.isLoggedIn
              ? '按日期、场馆、场地、时段依次选，价格与折扣在下单前就写清楚。'
              : '累计消费满 ¥500 自动升银卡（95 折），满 ¥2000 升金卡（90 折），折扣写进订单快照。'
          }}
        </p>
        <div class="closing-actions drop-in" style="--i: 2">
          <el-button type="primary" size="large" class="fx-border-glow fx-press" @click="startBooking">
            {{ userStore.isLoggedIn ? '开始预约' : '注册账号' }}
            <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>
          <el-button v-if="!userStore.isLoggedIn" size="large" @click="router.push('/login')">
            已有账号，登录
          </el-button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight } from '@element-plus/icons-vue'
import { useUserStore } from '@/store'
import { venueApi } from '@/api/venues'
import { announcementApi } from '@/api/announcements'
import CourtScene from '@/components/brand/CourtScene.vue'
import { asContactSheet, coverUrl, districtOf, hideBrokenImage } from '@/utils/venueVisual'

const router = useRouter()
const userStore = useUserStore()

const venues = ref([])
const announcements = ref([])

const sheet = computed(() => asContactSheet(venues.value))
const totalVenues = computed(() => venues.value.length || 5)
const totalCourts = computed(
  () => venues.value.reduce((n, v) => n + (v.court_count || 0), 0) || 24
)

// 逐字揭开用：中文按字拆（没有空格可拆）
const titleA = [...'把今晚的场，']
const titleB = [...'提前订下来。']

const pad = (n) => String(n).padStart(2, '0')
const shortDate = (t) => (t || '').slice(5, 10).replace('-', '/')

function startBooking() {
  if (!userStore.isLoggedIn) return router.push('/register')
  if (userStore.isAdmin) return router.push('/admin/dashboard')
  if (userStore.isReception) return router.push('/reception/dashboard')
  return router.push('/venues')
}

/** 印相表格子：游客点进去先登录（场馆详情与可预约时段需要登录） */
function openVenue(v) {
  if (!userStore.isLoggedIn) return router.push('/login')
  router.push(`/venues/${v.id}`)
}

onMounted(async () => {
  try {
    const res = await announcementApi.list({ page_size: 5 })
    announcements.value = (res.results || []).filter((a) => a.is_published !== false)
  } catch {
    // 公告接口异常不影响首页
  }

  // 场馆：登录了走完整接口；没登录走公开接口（只有场馆基础信息，拿不到可预约时段）
  try {
    const res = userStore.isLoggedIn
      ? await venueApi.list({ page_size: 50 })
      : await venueApi.publicList({ page_size: 50 })
    venues.value = res.results || res || []
  } catch {
    // 接口异常时退回"锁住的印相表"
  }
})
</script>

<style scoped>
.member-home {
  width: 100%;
}

/* ---------- 首屏 ---------- */

.hero {
  position: relative;
  display: flex;
  align-items: center;
  min-height: min(calc(92dvh - var(--nav-h)), 780px);
  padding: 64px 24px 72px;
  overflow: clip;
}

.hero-inner {
  position: relative;
  z-index: 3;
  width: 100%;
  max-width: 1180px;
  margin: 0 auto;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
}

.hero-kicker {
  margin: 0 0 20px;
  font-size: var(--fs-12);
  font-weight: 600;
  letter-spacing: 0.16em;
  color: var(--accent);
  text-transform: none;
}

.hero-title {
  max-width: 16ch;
  color: var(--ink-1);
  text-shadow: 0 1px 26px rgba(255, 255, 255, 0.7);
}

.hero-lede {
  margin-top: 20px;
  color: var(--ink-2);
  max-width: 40ch;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 18px;
  flex-wrap: wrap;
  margin-top: 32px;
}

.hero-cta {
  height: 52px;
  padding: 0 28px;
  font-size: var(--fs-16);
}

.link-ghost {
  border: 0;
  background: none;
  padding: 8px 2px;
  color: var(--ink-2);
  font-size: var(--fs-14);
  font-weight: 600;
  cursor: pointer;
  border-bottom: 1px solid var(--border-strong);
  transition: color var(--dur-2) var(--ease-out), border-color var(--dur-2) var(--ease-out);
}

.link-ghost:hover {
  color: var(--accent);
  border-color: var(--accent);
}

.steps {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 40px 0 0;
  padding: 0;
  list-style: none;
  font-size: var(--fs-12);
  letter-spacing: 0.08em;
  color: var(--ink-3);
}

.steps li {
  display: flex;
  align-items: center;
  gap: 10px;
}

.steps li + li::before {
  content: "";
  width: 26px;
  height: 1px;
  background: var(--border-strong);
}

/* ---------- 规格带 ---------- */

.band-section {
  width: 100%;
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 24px;
}

.band-section .spec-band {
  margin-top: 28px;
}

/* ---------- 印相表 ---------- */

.sheet-section,
.bulletin-section {
  width: 100%;
  max-width: 1180px;
  margin: 0 auto;
  padding: 56px 24px 0;
}

.section-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 20px;
}

.section-sub {
  margin: 8px 0 0;
  font-size: var(--fs-13);
  line-height: var(--lh-body);
  color: var(--ink-3);
  max-width: 52ch;
}

.section-count {
  font-size: var(--fs-12);
  font-weight: 700;
  letter-spacing: 0.1em;
  color: var(--ink-4);
  white-space: nowrap;
  padding-bottom: 4px;
}

.frame__addr {
  font-size: var(--fs-12);
  color: var(--ink-4);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
}

.frame__go {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: var(--fs-12);
  font-weight: 700;
  color: var(--accent);
  white-space: nowrap;
}

.sheet-locked {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 28px;
  flex-wrap: wrap;
  padding: 30px 28px;
  border: 1px dashed var(--border-strong);
  border-radius: var(--radius);
  background: var(--surface);
}

.locked-copy {
  min-width: 0;
  flex: 1 1 340px;
}

.locked-actions {
  display: flex;
  gap: 12px;
  flex: 0 0 auto;
}

/* ---------- 收尾换幕 ---------- */

.closing {
  margin-top: 64px;
  padding: 76px 24px;
}

.closing-inner {
  width: 100%;
  max-width: 1180px;
  margin: 0 auto;
}

.closing-lede {
  margin-top: 18px;
}

.closing-actions {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  margin-top: 30px;
}

/* ---------- 动效升级（2026-10） ---------- */

/* 名单跑马灯：两半等宽，靠每个格子自带右间距来保证 -50% 无缝 */
.ticker-section {
  width: 100%;
  max-width: 1180px;
  margin: 30px auto 0;
  padding: 0 24px;
}

.ticker {
  --fx-speed: 46s;
  --fx-gap: 38px;
  padding: 11px 0;
  border-top: 1px solid var(--border-soft);
  border-bottom: 1px solid var(--border-soft);
}

.ticker .fx-marquee__track {
  gap: 0;
}

.ticker__item {
  display: inline-flex;
  align-items: baseline;
  gap: 9px;
  padding-right: var(--fx-gap);
  font-size: var(--fs-12);
  letter-spacing: 0.04em;
  color: var(--ink-3);
  white-space: nowrap;
}

.ticker__item b {
  color: var(--accent);
  font-weight: 700;
  letter-spacing: 0.16em;
}

.ticker__item em {
  font-style: normal;
  color: var(--ink-4);
}

/* 区段标题下的发丝线：滚动时从左向右画出来 */
.section-head {
  position: relative;
  padding-bottom: 14px;
}

.section-head::after {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 1px;
  background: linear-gradient(90deg, var(--accent-line), var(--border) 42%, transparent);
  transform-origin: left center;
}

@media (prefers-reduced-motion: no-preference) {
  @supports (animation-timeline: view()) {
    .section-head::after {
      animation: home-rule-grow linear both;
      animation-timeline: view();
      animation-range: entry 0% cover 22%;
    }
  }
}

@keyframes home-rule-grow {
  from {
    transform: scaleX(0);
  }
  to {
    transform: scaleX(1);
  }
}

/* 规格带：悬停时数字换上主蓝，格底轻轻亮一下 */
.spec {
  transition: background-color var(--dur-3) var(--ease-out);
}

.spec__num {
  transition: color var(--dur-3) var(--ease-out);
}

@media (hover: hover) and (pointer: fine) {
  .spec:hover {
    background-color: var(--surface-2);
  }

  .spec:hover .spec__num {
    color: var(--accent);
  }
}

/* 公告行：左侧蓝条随悬停长出来 */
.bulletin__item {
  position: relative;
  transition: background-color var(--dur-2) var(--ease-out);
}

.bulletin__item::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 2px;
  background: var(--accent);
  transform: scaleY(0);
  transform-origin: top center;
  transition: transform var(--dur-3) var(--ease-out);
}

@media (hover: hover) and (pointer: fine) {
  .bulletin__item:hover {
    background-color: var(--surface-2);
  }

  .bulletin__item:hover::before {
    transform: scaleY(1);
  }
}

/* 收尾换幕：极光层压在正文下面 */
.closing {
  position: relative;
  isolation: isolate;
  overflow: clip;
}

.closing-inner {
  position: relative;
  z-index: 2;
}

/* 印相表格子：悬停时格号从灰变亮，像底片边缘被灯照到 */
.frame__no {
  transition: color var(--dur-3) var(--ease-out), border-color var(--dur-3) var(--ease-out);
}

@media (hover: hover) and (pointer: fine) {
  .frame--link:hover .frame__no {
    color: #ffffff;
    border-color: rgba(91, 157, 255, 0.7);
  }
}

/* ---------- 断点 ---------- */

@media (max-width: 900px) {
  .hero {
    min-height: auto;
    padding: 44px 20px 56px;
  }

  .hero-title {
    max-width: none;
  }

  .steps {
    margin-top: 30px;
  }

  .sheet-section,
  .bulletin-section {
    padding-top: 44px;
  }

  .closing {
    padding: 56px 20px;
  }
}

@media (max-width: 560px) {
  .hero-cta {
    width: 100%;
    justify-content: center;
  }

  .hero-actions {
    gap: 12px;
  }

  .sheet-locked {
    padding: 22px 18px;
  }

  .locked-actions {
    width: 100%;
  }

  .locked-actions :deep(.el-button) {
    flex: 1;
  }
}
</style>
