<template>
  <div class="page">
    <div class="detail-toolbar">
      <el-button round @click="$router.push('/activities')">
        <el-icon class="el-icon--left"><Back /></el-icon>返回活动列表
      </el-button>
    </div>

    <div v-if="loading" class="surface detail-loading">
      <el-skeleton :rows="6" animated />
    </div>

    <template v-else-if="activity">
      <section class="surface head fx-rise" style="--i: 0">
        <div class="head-top">
          <div class="head-tags">
            <el-tag size="small" round effect="light">{{ typeLabel(activity.type) }}</el-tag>
            <el-tag v-if="!activity.is_active" type="info" size="small" round effect="light">未开放</el-tag>
            <el-tag v-if="myStatus" :type="statusTag(myStatus)" size="small" round effect="light">
              {{ statusLabel(myStatus) }}
            </el-tag>
          </div>
          <h1>{{ activity.title }}</h1>
        </div>

        <p class="desc">{{ activity.description || '暂无说明' }}</p>

        <div class="facts">
          <div class="fact">
            <span class="fact-label">场馆</span>
            <span class="fact-value">{{ activity.venue_name }}</span>
          </div>
          <div class="fact">
            <span class="fact-label">活动时间</span>
            <span class="fact-value mono">{{ fmt(activity.start_at) }} ~ {{ fmt(activity.end_at) }}</span>
          </div>
          <div class="fact">
            <span class="fact-label">报名截止</span>
            <span class="fact-value mono">{{ fmt(activity.deadline) }}</span>
          </div>
          <div class="fact">
            <span class="fact-label">报名费</span>
            <span class="fact-value mono accent">¥{{ money(activity.price) }}</span>
          </div>
          <div class="fact fact--wide">
            <span class="fact-label fx-tabular">报名进度 {{ activity.registered }}/{{ activity.capacity }}</span>
            <el-progress
              :percentage="pct"
              :stroke-width="10"
              :status="pct >= 100 ? 'exception' : undefined"
              :show-text="false"
            />
          </div>
        </div>

        <div class="head-actions">
          <el-button v-if="canRegister" type="primary" round class="fx-border-glow fx-press" :loading="acting" @click="register">
            立即报名
          </el-button>
          <el-button v-else-if="myStatus === 'registered'" type="info" round :loading="acting" @click="cancelReg">
            取消报名
          </el-button>
          <el-button v-else type="info" round disabled>{{ disabledReason }}</el-button>
        </div>
      </section>

      <section class="surface rules fx-reveal-clip">
        <h2>参与须知</h2>
        <ul>
          <li>报名成功后请按时到场，入场时由前台在名单中签到核销。</li>
          <li>报名截止后不可报名；取消报名会自动释放名额，可重新报名。</li>
          <li>免费活动（¥0）同样需要报名占位。</li>
        </ul>
      </section>
    </template>

    <div v-else class="surface empty-state">
      <strong>活动不存在</strong>
      <span>它可能已被删除，或者链接里的编号不对。</span>
      <el-button round @click="$router.push('/activities')">回到活动列表</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Back } from '@element-plus/icons-vue'
import { activityApi } from '@/api/activities'
import { money } from '@/utils/format'

const route = useRoute()
const activity = ref(null)
const loading = ref(true)
const acting = ref(false)

const typeLabel = (t) => ({ match: '比赛', training: '培训', coach: '教练课' }[t] || t)
const statusLabel = (s) => ({ registered: '已报名', cancelled: '已取消', attended: '已到场' }[s] || s)
const statusTag = (s) => ({ registered: 'success', cancelled: 'info', attended: 'warning' }[s] || 'info')
const fmt = (t) => (t || '').slice(0, 16).replace('T', ' ')

const myStatus = computed(() => activity.value?.my_registration?.status || null)
const pct = computed(() => {
  const a = activity.value
  if (!a || !a.capacity) return 0
  return Math.min(100, Math.round((Number(a.registered) / Number(a.capacity)) * 100))
})
const canRegister = computed(() => {
  const a = activity.value
  if (!a || !a.is_active) return false
  if (new Date() > new Date(a.deadline)) return false
  if (Number(a.registered) >= Number(a.capacity)) return false
  return myStatus.value !== 'registered'
})
const disabledReason = computed(() => {
  const a = activity.value
  if (!a) return ''
  if (!a.is_active) return '活动未开放'
  if (new Date() > new Date(a.deadline)) return '已过报名截止'
  if (Number(a.registered) >= Number(a.capacity)) return '名额已满'
  if (myStatus.value === 'cancelled') return '已取消报名'
  if (myStatus.value === 'attended') return '已到场'
  return ''
})

async function fetchData() {
  loading.value = true
  try {
    activity.value = await activityApi.detail(route.params.id)
  } catch {
    activity.value = null
  } finally {
    loading.value = false
  }
}

async function register() {
  acting.value = true
  try {
    await activityApi.register(activity.value.id)
    ElMessage.success('报名成功')
    fetchData()
  } catch { /* 拦截器已提示 */ } finally {
    acting.value = false
  }
}

async function cancelReg() {
  try {
    await ElMessageBox.confirm('确定取消报名吗？取消后会释放名额。', '取消报名', { type: 'warning' })
  } catch { return }
  acting.value = true
  try {
    await activityApi.cancel(activity.value.id)
    ElMessage.success('已取消报名')
    fetchData()
  } catch { /* 拦截器已提示 */ } finally {
    acting.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.page { width: 100%; max-width: 1080px; margin: 0 auto; padding: 24px 24px 80px; }
.detail-toolbar { margin-bottom: 14px; }
.detail-loading { padding: 28px; }
.head { padding: 26px 28px; }
.head-tags { display: flex; gap: 8px; margin-bottom: 10px; flex-wrap: wrap; }
.head-top h1 { margin: 0; font-size: var(--fs-24); font-weight: 800; color: var(--ink-1); }
.desc { margin: 8px 0 18px; color: var(--ink-2); font-size: var(--fs-14); line-height: 1.7; white-space: pre-wrap; }
.facts { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px 22px; }
.fact { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.fact--wide { grid-column: 1 / -1; }
.fact-label { font-size: var(--fs-12); font-weight: 700; color: var(--ink-4); }
.fact-value { font-size: var(--fs-14); color: var(--ink-1); overflow-wrap: anywhere; }
.head-actions { margin-top: 20px; }
.rules { margin-top: 14px; padding: 22px 28px; }
.rules h2 { margin: 0 0 10px; font-size: var(--fs-16); color: var(--ink-1); }
.rules ul { margin: 0; padding-left: 18px; color: var(--ink-3); font-size: var(--fs-13); line-height: 1.9; }
.empty-state { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 40px 20px; color: var(--ink-3); }
.empty-state strong { font-size: var(--fs-16); color: var(--ink-1); }
.accent { color: var(--accent); }

/* ==========================================================================
   2026-10 动效层：进度条渐变 + 主 CTA 描边光（只加 class 与过渡）
   ========================================================================== */

/* 报名进度：主蓝到青的渐变；名额满时仍走 EP 的红色异常态（不覆盖它） */
.facts :deep(.el-progress:not(.is-exception) .el-progress-bar__inner) {
  background-image: linear-gradient(90deg, var(--accent) 0%, var(--accent-2) 100%);
}

@media (prefers-reduced-motion: no-preference) {
  /* 进度从 0 长到当前值：宽度仍由 EP 控制，这里只补一个进场 */
  .facts :deep(.el-progress-bar__inner) {
    transition: width var(--dur-5) var(--ease-expo);
    transform-origin: left center;
    animation: ad-progress-grow var(--dur-6) var(--ease-expo) both;
  }

  @keyframes ad-progress-grow {
    from {
      transform: scaleX(0);
    }
    to {
      transform: scaleX(1);
    }
  }

  /* 主 CTA：按下时比 EP 默认更实一点，让描边光有"被按下去"的回应 */
  .head-actions :deep(.fx-press:active) {
    transform: scale(0.97);
  }
}
</style>
