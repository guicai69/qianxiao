<template>
  <div class="page">
    <header class="page-head fx-rise">
      <h1>优惠券与积分</h1>
      <p>
        当前积分 <b class="mono accent">×{{ points }}</b>
        · 500 积分兑换 ¥5 券（30 天有效）· 支付/充值 1 元积 1 分
      </p>
      <el-button type="primary" round class="fx-press" :disabled="points < 500" @click="redeem">兑换 ¥5 券</el-button>
    </header>

    <h2 class="sub">可领取</h2>
    <div class="list surface claimable-list">
      <div v-if="!claimable.length" class="empty">暂无可用券</div>
      <section v-for="c in claimable" :key="c.id" class="card fx-sheen">
        <div class="card-main">
          <h3>{{ c.name }} <b class="mono accent">¥{{ money(c.amount) }}</b></h3>
          <p class="meta mono">
            满 ¥{{ money(c.min_amount) }} 可用 · 已领 {{ c.claimed }}/{{ c.total }}
            · {{ fmt(c.expires_at) }} 前有效
          </p>
        </div>
        <el-button type="primary" round class="fx-press" :disabled="c.claimed >= c.total" @click="claim(c)">领取</el-button>
      </section>
    </div>

    <h2 class="sub">我的券</h2>
    <div class="chips">
      <button
        v-for="t in mineTabs"
        :key="t.key"
        type="button"
        class="chip fx-press"
        :class="{ active: mineFilter === t.key }"
        @click="mineFilter = t.key; fetchMine()"
      >
        {{ t.label }}
      </button>
    </div>
    <div class="list surface mine-list" :key="mine.map((c) => c.id).join('-')">
      <div v-if="!mine.length" class="empty">该分类下还没有券</div>
      <section
        v-for="u in mine"
        :key="u.id"
        class="card fx-sheen"
        :class="[`is-${u.expiry_status}`, { 'is-expired': u.expiry_status === 'expired' }]"
      >
        <div class="card-main">
          <h3>
            {{ u.coupon_name || '积分兑换券' }} <b class="mono accent">¥{{ money(u.amount) }}</b>
            <el-tag :type="expiryTag(u.expiry_status)" size="small" round effect="light" class="state-tag">
              {{ expiryLabel(u.expiry_status) }}
            </el-tag>
          </h3>
          <p class="meta mono">
            满 ¥{{ money(u.min_amount) }} 可用 · {{ fmt(u.expires_at) }} 前有效
            <span v-if="u.expiry_status === 'expired'">· 已过期不可用</span>
          </p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { couponApi } from '@/api/coupons'
import { money } from '@/utils/format'
import { useUserStore } from '@/store'

const userStore = useUserStore()
const claimable = ref([])
const mine = ref([])
const mineFilter = ref('')
const points = computed(() => Number(userStore.userInfo?.points || 0))
const fmt = (t) => (t || '').slice(0, 16).replace('T', ' ')

const mineTabs = [
  { key: '', label: '全部' },
  { key: 'unused', label: '可用' },
  { key: 'used', label: '已使用' },
  { key: 'expired', label: '已过期' },
]
const expiryLabel = (s) => ({ unused: '可用', used: '已使用', expired: '已过期' }[s] || s)
const expiryTag = (s) => ({ unused: 'success', used: 'info', expired: 'danger' }[s] || 'info')

async function fetchClaimable() {
  try {
    const res = await couponApi.list()
    claimable.value = res.results || []
  } catch {
    ElMessage.error('获取优惠券失败')
  }
}

async function fetchMine() {
  try {
    const res = await couponApi.my(mineFilter.value ? { status: mineFilter.value } : {})
    mine.value = res.data || []
  } catch {
    ElMessage.error('获取我的券失败')
  }
}

function fetchData() {
  fetchClaimable()
  fetchMine()
}

async function claim(c) {
  try {
    await couponApi.claim(c.id)
    ElMessage.success('领取成功')
    fetchData()
  } catch { /* 拦截器已提示 */ }
}

async function redeem() {
  try {
    const res = await couponApi.redeem()
    userStore.setUserInfo({ ...userStore.userInfo, points: res.data.points })
    ElMessage.success('兑换成功')
    fetchData()
  } catch { /* 拦截器已提示 */ }
}

onMounted(fetchData)
</script>

<style scoped>
.page { width: 100%; max-width: 1080px; margin: 0 auto; padding: 24px 24px 80px; }
.page-head h1 { font-size: var(--fs-24); font-weight: 800; color: var(--ink-1); margin: 0; }
.page-head p { margin: 6px 0 12px; color: var(--ink-3); font-size: var(--fs-13); }
.sub { margin: 28px 0 12px; font-size: var(--fs-16); color: var(--ink-1); }
.chips { display: flex; gap: 8px; margin: 0 0 12px; }
.chip { padding: 6px 14px; border: 1px solid var(--border); border-radius: 999px; background: var(--surface); cursor: pointer; font-size: var(--fs-13); color: var(--ink-2); }
.chip.active { border-color: var(--accent); color: var(--accent); background: var(--accent-soft); font-weight: 700; }
.list { padding: 10px 18px; }
.empty { padding: 28px 0; text-align: center; color: var(--ink-4); font-size: var(--fs-13); }
.card { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 16px 0; border-bottom: 1px solid var(--border-soft); }
.card:last-child { border-bottom: 0; }
.card.is-expired { opacity: 0.55; }
.card-main { min-width: 0; }
.card-main h3 { margin: 0 0 6px; font-size: var(--fs-15); color: var(--ink-1); display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.state-tag { flex: 0 0 auto; }
.meta { margin: 0; color: var(--ink-4); font-size: var(--fs-12); }

/* ---------- 动效升级（2026-10）：票券质感 ---------- */

.page-head.fx-rise {
  --i: 0;
}

/* 券柜：把柜台压暗一档，券才像浮在上面 */
.claimable-list,
.mine-list {
  padding: 14px;
  background: var(--sunken);
}

/* 券本体：抬起来的一张纸 */
.card {
  position: relative;
  margin: 0 0 10px;
  padding: 15px 18px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: linear-gradient(180deg, var(--surface) 0%, var(--surface-2) 100%);
  box-shadow: var(--shadow);
  transition: border-color var(--dur-2) var(--ease-out), box-shadow var(--dur-3) var(--ease-out);
}

.card:last-child {
  margin-bottom: 0;
  border-bottom: 1px solid var(--border);
}

/* 两侧打孔：露出来的就是券柜底色，票券的「根」 */
.card::before {
  content: "";
  position: absolute;
  left: -1px;
  right: -1px;
  top: 50%;
  height: 18px;
  margin-top: -9px;
  background: radial-gradient(circle at 0 50%, var(--sunken) 0 7.5px, transparent 8px),
    radial-gradient(circle at 100% 50%, var(--sunken) 0 7.5px, transparent 8px);
  pointer-events: none;
}

/* 可用：右上角一层很淡的蓝光，边线跟主色走 */
.card.is-unused {
  border-color: var(--accent-line);
  background: radial-gradient(130% 150% at 100% 0%, var(--accent-soft) 0%, transparent 55%),
    linear-gradient(180deg, var(--surface) 0%, var(--surface-2) 100%);
}

/* 已使用：退成灰纸，只留形状 */
.card.is-used {
  border-color: var(--border-soft);
  background: var(--surface-2);
  box-shadow: none;
}

/* 已过期：虚线边 + 整体降饱和 */
.card.is-expired {
  opacity: 0.82;
  border-style: dashed;
  border-color: var(--border-strong);
  background: var(--surface-2);
  box-shadow: none;
}

.card.is-used .card-main h3,
.card.is-expired .card-main h3 {
  color: var(--ink-3);
}

.card.is-used .card-main h3 b,
.card.is-expired .card-main h3 b {
  color: var(--ink-4);
}

.card-main h3 b {
  font-size: var(--fs-16);
  font-weight: 800;
  letter-spacing: -0.02em;
}

.card.is-unused .card-main h3 b {
  color: var(--accent);
}

@media (hover: hover) and (pointer: fine) {
  .card:hover {
    border-color: var(--accent-line);
    box-shadow: var(--shadow-md);
  }

  .card.is-expired:hover {
    border-color: var(--border-strong);
    box-shadow: none;
  }
}

/* 按钮：按下内缩（fx-press 只过渡 transform，这里补回颜色/投影，别让 EP 的底色变硬切） */
.el-button.fx-press {
  transition: transform var(--dur-2) var(--ease-out), background-color var(--dur-2) var(--ease-out),
    border-color var(--dur-2) var(--ease-out), box-shadow var(--dur-2) var(--ease-out),
    color var(--dur-2) var(--ease-out);
}

/* 分类胶囊：按下内缩（补回颜色过渡） */
.chip.fx-press {
  transition: transform var(--dur-2) var(--ease-out), border-color var(--dur-2) var(--ease-out),
    color var(--dur-2) var(--ease-out), background-color var(--dur-2) var(--ease-out);
}

/* 入场：切分类时券柜重挂载（列表容器绑了 :key），券逐张落下 */
@media (prefers-reduced-motion: no-preference) {
  .card {
    animation: ticket-in var(--dur-4) var(--ease-expo) backwards;
    animation-delay: calc(var(--i, 0) * 55ms);
  }

  .card:nth-child(1) {
    --i: 0;
  }

  .card:nth-child(2) {
    --i: 1;
  }

  .card:nth-child(3) {
    --i: 2;
  }

  .card:nth-child(4) {
    --i: 3;
  }

  .card:nth-child(5) {
    --i: 4;
  }

  .card:nth-child(6) {
    --i: 5;
  }

  .card:nth-child(n + 7) {
    --i: 6;
  }

  @keyframes ticket-in {
    from {
      opacity: 0;
      transform: translateY(10px) scale(0.995);
    }

    to {
      opacity: 1;
      transform: none;
    }
  }
}

@media (max-width: 640px) {
  .claimable-list,
  .mine-list {
    padding: 10px;
  }

  .card {
    padding: 13px 14px;
  }
}
</style>
