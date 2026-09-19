<template>
  <!-- 走错门了：给一个球馆暗色平面，不是一张白色的系统报错页 -->
  <div class="not-found hall-section grain" data-plane="hall">
    <div class="nf-aura" aria-hidden="true"></div>

    <div class="nf-inner hall-inner">
      <div class="nf-copy">
        <span class="nf-code mono">404</span>
        <h1 class="display-2 nf-title">这块场地不存在</h1>
        <p class="lede nf-lede">
          地址可能输错了，或者这个页面已经撤下。回首页重新挑一座球馆、一片场地。
        </p>

        <div class="nf-actions">
          <el-button type="primary" size="large" @click="goHome">返回首页</el-button>
          <el-button size="large" @click="router.push('/venues')">浏览场馆</el-button>
        </div>
      </div>

      <svg class="nf-court" viewBox="0 0 610 1340" preserveAspectRatio="xMidYMid meet" aria-hidden="true">
        <g fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="square">
          <rect x="4" y="4" width="602" height="1332" />
          <line x1="4" y1="670" x2="606" y2="670" />
          <line x1="305" y1="4" x2="305" y2="1336" />
          <line x1="4" y1="472" x2="606" y2="472" />
          <line x1="4" y1="868" x2="606" y2="868" />
          <line x1="4" y1="76" x2="606" y2="76" />
          <line x1="4" y1="1264" x2="606" y2="1264" />
          <line x1="46" y1="4" x2="46" y2="1336" />
          <line x1="564" y1="4" x2="564" y2="1336" />
        </g>
      </svg>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router"
import { useUserStore } from "@/store"

const router = useRouter()
const userStore = useUserStore()

function goHome() {
  if (userStore.isAdmin) router.push("/admin/dashboard")
  else if (userStore.isReception) router.push("/reception/dashboard")
  else router.push("/")
}
</script>

<style scoped>
.not-found {
  display: flex;
  align-items: center;
  min-height: 100dvh;
  padding: 64px 24px;
}

/* 顶灯：只照亮标题那一块 */
.nf-aura {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  background: radial-gradient(58% 46% at 30% 22%, var(--accent-soft), transparent 72%);
}

.nf-inner {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 340px);
  align-items: center;
  gap: 48px;
  width: 100%;
  max-width: 1120px;
  margin: 0 auto;
}

.nf-copy {
  min-width: 0;
}

.nf-code {
  display: block;
  font-size: var(--fs-13);
  font-weight: 700;
  letter-spacing: 0.22em;
  color: var(--accent);
}

.nf-title {
  margin: 14px 0 0;
  color: var(--ink-1);
}

.nf-lede {
  margin-top: 16px;
  color: var(--ink-2);
  max-width: 40ch;
}

.nf-actions {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
  margin-top: 30px;
}

.nf-actions :deep(.el-button) {
  min-height: 44px;
  padding: 0 24px;
}

/* 次级按钮：Element 的默认底来自 :root 算出的纸面白，
   暗色平面下要按球馆令牌接回来，不然是一块白膏药 */
.nf-actions :deep(.el-button:not(.el-button--primary)) {
  --el-button-bg-color: var(--surface);
  --el-button-border-color: var(--border-strong);
  --el-button-text-color: var(--ink-1);
  --el-button-hover-bg-color: var(--surface-2);
  --el-button-hover-border-color: var(--ink-3);
  --el-button-hover-text-color: var(--ink-1);
  --el-button-active-bg-color: var(--surface-2);
  --el-button-active-border-color: var(--ink-3);
  --el-button-active-text-color: var(--ink-1);
}

/* 一块画在地面上的空场地：占住右边的空，不做无意义的装饰图形 */
.nf-court {
  width: 100%;
  max-height: 56vh;
  color: var(--border-strong);
  opacity: 0.75;
}

@media (max-width: 900px) {
  .nf-inner {
    grid-template-columns: minmax(0, 1fr);
    gap: 36px;
  }

  .nf-court {
    order: -1;
    max-width: 190px;
    max-height: 30vh;
    margin: 0 auto;
  }
}

@media (max-width: 640px) {
  .not-found {
    padding: 40px 16px;
  }

  .nf-actions :deep(.el-button) {
    flex: 1 1 100%;
    min-height: 46px;
  }
}
</style>
