<template>
  <div class="page">
    <header class="page-head">
      <h1>优惠券与积分</h1>
      <p>
        当前积分 <b class="mono accent">×{{ points }}</b>
        · 500 积分兑换 ¥5 券（30 天有效）· 支付/充值 1 元积 1 分
      </p>
      <el-button type="primary" round :disabled="points < 500" @click="redeem">兑换 ¥5 券</el-button>
    </header>

    <h2 class="sub">可领取</h2>
    <div class="list surface">
      <div v-if="!claimable.length" class="empty">暂无可用券</div>
      <section v-for="c in claimable" :key="c.id" class="card">
        <div class="card-main">
          <h3>{{ c.name }} <b class="mono accent">¥{{ money(c.amount) }}</b></h3>
          <p class="meta mono">
            满 ¥{{ money(c.min_amount) }} 可用 · 已领 {{ c.claimed }}/{{ c.total }}
            · {{ fmt(c.expires_at) }} 前有效
          </p>
        </div>
        <el-button type="primary" round :disabled="c.claimed >= c.total" @click="claim(c)">领取</el-button>
      </section>
    </div>

    <h2 class="sub">我的券</h2>
    <div class="list surface">
      <div v-if="!mine.length" class="empty">还没有券</div>
      <section v-for="u in mine" :key="u.id" class="card">
        <div class="card-main">
          <h3>{{ u.coupon_name || '积分兑换券' }} <b class="mono accent">¥{{ money(u.amount) }}</b></h3>
          <p class="meta mono">
            满 ¥{{ money(u.min_amount) }} 可用 · {{ fmt(u.expires_at) }} 前有效
            · {{ u.status === 'used' ? '已使用' : '未使用' }}
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
const points = computed(() => Number(userStore.userInfo?.points || 0))
const fmt = (t) => (t || '').slice(0, 16).replace('T', ' ')

async function fetchData() {
  try {
    const [list, my] = await Promise.all([couponApi.list(), couponApi.my()])
    claimable.value = list.results || []
    mine.value = my.data || []
  } catch {
    ElMessage.error('获取优惠券失败')
  }
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
.list { padding: 10px 18px; }
.empty { padding: 28px 0; text-align: center; color: var(--ink-4); font-size: var(--fs-13); }
.card { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 16px 0; border-bottom: 1px solid var(--border-soft); }
.card:last-child { border-bottom: 0; }
.card-main { min-width: 0; }
.card-main h3 { margin: 0 0 6px; font-size: var(--fs-15); color: var(--ink-1); }
.meta { margin: 0; color: var(--ink-4); font-size: var(--fs-12); }
</style>
