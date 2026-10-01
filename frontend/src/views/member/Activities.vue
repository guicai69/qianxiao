<template>
  <div class="page">
    <header class="page-head">
      <h1>活动与课程</h1>
      <p>比赛、培训、教练课统一报名；取消报名自动释放名额。</p>
    </header>

    <div class="chips">
      <button
        v-for="t in typeOptions"
        :key="t.key"
        type="button"
        class="chip"
        :class="{ active: activeType === t.key }"
        @click="activeType = t.key; fetchData()"
      >
        {{ t.label }}
      </button>
    </div>

    <div v-loading="loading" class="list surface">
      <div v-if="!items.length" class="empty">暂无活动</div>
      <section v-for="a in items" :key="a.id" class="card">
        <div class="card-main">
          <div class="card-top">
            <el-tag size="small" round effect="light">{{ typeLabel(a.type) }}</el-tag>
            <h3>{{ a.title }}</h3>
          </div>
          <p class="desc">{{ a.description || '暂无说明' }}</p>
          <div class="meta mono">
            <span>{{ a.venue_name }}</span>
            <span>{{ fmt(a.start_at) }} ~ {{ fmt(a.end_at) }}</span>
            <span>¥{{ money(a.price) }}</span>
            <span>名额 {{ a.registered }}/{{ a.capacity }}</span>
          </div>
        </div>
        <div class="card-side">
          <el-button v-if="myStatus(a.id) === 'registered'" type="info" round @click="cancel(a)">
            取消报名
          </el-button>
          <el-button v-else type="primary" round :disabled="a.registered >= a.capacity" @click="register(a)">
            报名
          </el-button>
        </div>
      </section>
    </div>

    <h2 class="sub">我的报名</h2>
    <div class="list surface">
      <div v-if="!mine.length" class="empty">还没有报名记录</div>
      <section v-for="r in mine" :key="r.id" class="card">
        <div class="card-main">
          <div class="card-top">
            <el-tag size="small" round effect="light">{{ r.activity_title }}</el-tag>
            <el-tag size="small" round effect="plain">{{ statusLabel(r.status) }}</el-tag>
          </div>
          <div class="meta mono">
            <span>¥{{ money(r.price) }}</span>
            <span>{{ fmt(r.created_at) }}</span>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { activityApi } from '@/api/activities'
import { money } from '@/utils/format'

const items = ref([])
const mine = ref([])
const loading = ref(false)
const activeType = ref('')

const typeOptions = [
  { key: '', label: '全部' },
  { key: 'match', label: '比赛' },
  { key: 'training', label: '培训' },
  { key: 'coach', label: '教练课' },
]
const typeLabel = (t) => ({ match: '比赛', training: '培训', coach: '教练课' }[t] || t)
const statusLabel = (s) => ({ registered: '已报名', cancelled: '已取消', attended: '已到场' }[s] || s)
const fmt = (t) => (t || '').slice(0, 16).replace('T', ' ')

const myStatus = computed(() => {
  const map = {}
  for (const r of mine.value) map[r.activity] = r.status
  return (id) => map[id]
})

async function fetchData() {
  loading.value = true
  try {
    const params = {}
    if (activeType.value) params.type = activeType.value
    const [list, my] = await Promise.all([activityApi.list(params), activityApi.my()])
    items.value = list.results || []
    mine.value = my.data || []
  } catch {
    ElMessage.error('获取活动失败')
  } finally {
    loading.value = false
  }
}

async function register(a) {
  try {
    await activityApi.register(a.id)
    ElMessage.success('报名成功')
    fetchData()
  } catch { /* 拦截器已提示 */ }
}

async function cancel(a) {
  try {
    await activityApi.cancel(a.id)
    ElMessage.success('已取消报名')
    fetchData()
  } catch { /* 拦截器已提示 */ }
}

onMounted(fetchData)
</script>

<style scoped>
.page { width: 100%; max-width: 1080px; margin: 0 auto; padding: 24px 24px 80px; }
.page-head h1 { font-size: var(--fs-24); font-weight: 800; color: var(--ink-1); margin: 0; }
.page-head p { margin: 6px 0 0; color: var(--ink-3); font-size: var(--fs-13); }
.chips { display: flex; gap: 8px; margin: 18px 0 14px; }
.chip { padding: 6px 14px; border: 1px solid var(--border); border-radius: 999px; background: var(--surface); cursor: pointer; font-size: var(--fs-13); color: var(--ink-2); }
.chip.active { border-color: var(--accent); color: var(--accent); background: var(--accent-soft); font-weight: 700; }
.list { padding: 10px 18px; }
.empty { padding: 28px 0; text-align: center; color: var(--ink-4); font-size: var(--fs-13); }
.card { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 16px 0; border-bottom: 1px solid var(--border-soft); }
.card:last-child { border-bottom: 0; }
.card-main { min-width: 0; }
.card-top { display: flex; align-items: center; gap: 10px; }
.card-top h3 { margin: 0; font-size: var(--fs-15); color: var(--ink-1); }
.desc { margin: 6px 0; color: var(--ink-3); font-size: var(--fs-13); }
.meta { display: flex; flex-wrap: wrap; gap: 6px 14px; color: var(--ink-4); font-size: var(--fs-12); }
.sub { margin: 28px 0 12px; font-size: var(--fs-16); color: var(--ink-1); }
</style>
