<template>
  <div class="venue-list-wrapper">
    <header class="page-header list-head">
      <div>
        <h2>选择场馆</h2>
        <p>点开一座球馆，查看场地与可预约时段</p>
      </div>
      <span class="list-count mono">{{ filtered.length }} 座</span>
    </header>

    <div class="list-toolbar">
      <el-input
        v-model="search"
        placeholder="搜索场馆名称或地址"
        clearable
        :prefix-icon="Search"
        class="search-input"
      />
      <span class="toolbar-hint mono">共 {{ venues.length }} 座球馆</span>
    </div>

    <div v-if="loading" class="skeleton-block surface">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else-if="filtered.length === 0" class="surface empty-state">
      <strong>没有匹配的球馆</strong>
      <span>换个关键词试试，或者清空搜索框看全部 {{ venues.length }} 座球馆。</span>
    </div>

    <TransitionGroup v-else name="row" tag="div" class="venue-rows" appear>
      <article
        v-for="venue in filtered"
        :key="venue.id"
        class="venue-row"
        role="button"
        tabindex="0"
        @click="selectVenue(venue)"
        @keyup.enter="selectVenue(venue)"
      >
        <div class="row-cover">
          <img
            :src="coverUrl(venue)"
            :alt="`${venue.name}室内球场`"
            loading="lazy"
            decoding="async"
            @error="hideBrokenImage"
          />
          <span class="row-cover-grade"></span>
          <span class="row-no mono">{{ venue.no }}</span>
        </div>

        <div class="row-body">
          <div class="row-title">
            <h3>{{ venue.name }}</h3>
            <el-tag :type="venue.is_active ? 'success' : 'info'" effect="light" size="small" round>
              {{ venue.is_active ? '营业中' : '已停用' }}
            </el-tag>
          </div>

          <dl class="row-facts">
            <div>
              <dt>地址</dt>
              <dd>{{ venue.address || '暂无地址' }}</dd>
            </div>
            <div>
              <dt>电话</dt>
              <dd class="mono">{{ venue.phone || '暂无电话' }}</dd>
            </div>
            <div>
              <dt>场地</dt>
              <dd class="mono">{{ venue.court_count || 0 }} 片</dd>
            </div>
          </dl>
        </div>

        <div class="row-action">
          <span class="row-price mono">¥30<small>起</small></span>
          <span class="row-go">
            查看场地
            <el-icon><ArrowRight /></el-icon>
          </span>
        </div>
      </article>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, ArrowRight } from '@element-plus/icons-vue'
import { venueApi } from '@/api/venues'
import { asContactSheet, coverUrl, hideBrokenImage } from '@/utils/venueVisual'

const router = useRouter()
const venues = ref([])
const loading = ref(true)
const search = ref('')

// 用首页同一套编号与封面，列表顺序跟着编号走，05 不会排到 01 前面
const sheet = computed(() => asContactSheet(venues.value))

const filtered = computed(() => {
  if (!search.value) return sheet.value
  const q = search.value.toLowerCase()
  return sheet.value.filter(
    (v) => v.name.toLowerCase().includes(q) || (v.address || '').toLowerCase().includes(q)
  )
})

async function fetchVenues() {
  try {
    const res = await venueApi.list({ page_size: 100 })
    venues.value = res.results || []
  } catch (e) {
    console.warn('Fetch venues failed:', e)
  } finally {
    loading.value = false
  }
}

function selectVenue(venue) {
  router.push('/venues/' + venue.id)
}

onMounted(fetchVenues)
</script>

<style scoped>
.venue-list-wrapper {
  width: 100%;
  max-width: 1080px;
  margin: 0 auto;
  padding: 28px 24px 72px;
}

.list-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
}

.list-count {
  font-size: var(--fs-12);
  font-weight: 700;
  letter-spacing: 0.12em;
  color: var(--ink-4);
  padding-bottom: 4px;
}

.list-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin: 22px 0 18px;
}

.search-input {
  max-width: 380px;
}

.toolbar-hint {
  font-size: var(--fs-12);
  color: var(--ink-4);
  white-space: nowrap;
}

.skeleton-block {
  padding: 24px;
}

/* ---------- 行式列表：跟首页的印相表格子刻意用不同排版家族 ---------- */

.venue-rows {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.venue-row {
  display: grid;
  grid-template-columns: 216px minmax(0, 1fr) auto;
  min-height: 144px;
  align-items: stretch;
  gap: 0;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  overflow: hidden;
  cursor: pointer;
  transition: transform var(--dur-3) var(--ease-out), box-shadow var(--dur-3) var(--ease-out),
    border-color var(--dur-3) var(--ease-out);
}

.row-cover {
  position: relative;
  aspect-ratio: 3 / 2;
  overflow: hidden;
  background-color: #e3ecf9;
  background-image:
    linear-gradient(90deg, transparent calc(50% - 1px), rgba(26, 95, 208, 0.2) 50%, transparent calc(50% + 1px)),
    radial-gradient(60% 50% at 50% 50%, rgba(26, 95, 208, 0.1), transparent 72%);
}

.row-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: saturate(0.92) contrast(1.05) brightness(1.02);
  transition: transform var(--dur-4) var(--ease-out);
}

.row-cover-grade {
  position: absolute;
  inset: 0;
  pointer-events: none;
  mix-blend-mode: multiply;
  background: linear-gradient(180deg, rgba(20, 44, 96, 0.03) 0%, rgba(16, 32, 64, 0.28) 100%);
}

.row-no {
  position: absolute;
  top: 10px;
  left: 11px;
  z-index: 2;
  padding: 3px 8px;
  border-radius: 999px;
  background: rgba(16, 32, 64, 0.58);
  border: 1px solid rgba(255, 255, 255, 0.16);
  color: #f4f6f1;
  font-size: var(--fs-11);
  font-weight: 700;
  letter-spacing: 0.12em;
}

.row-body {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 14px;
  padding: 20px 22px;
  min-width: 0;
}

.row-title {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.row-title h3 {
  font-size: var(--fs-18);
  font-weight: 800;
  letter-spacing: -0.015em;
  color: var(--ink-1);
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.row-facts {
  display: flex;
  gap: 26px;
  flex-wrap: wrap;
  margin: 0;
}

.row-facts dt {
  font-size: var(--fs-11);
  font-weight: 700;
  letter-spacing: 0.1em;
  color: var(--ink-4);
  margin-bottom: 4px;
}

.row-facts dd {
  margin: 0;
  font-size: var(--fs-13);
  color: var(--ink-2);
  max-width: 30ch;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.row-action {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: center;
  gap: 10px;
  padding: 20px 22px;
  border-left: 1px solid var(--border-soft);
  min-width: 168px;
}

.row-price {
  font-size: var(--fs-18);
  font-weight: 700;
  color: var(--accent);
  white-space: nowrap;
}

.row-price small {
  font-size: 0.6em;
  color: var(--ink-3);
  margin-left: 2px;
}

.row-go {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: var(--fs-12);
  font-weight: 700;
  color: var(--ink-3);
  white-space: nowrap;
  transition: color var(--dur-2) var(--ease-out);
}

@media (hover: hover) and (pointer: fine) {
  .venue-row:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
    border-color: var(--border-strong);
  }

  .venue-row:hover .row-cover img {
    transform: scale(1.04);
  }

  .venue-row:hover .row-go {
    color: var(--accent);
  }
}

/* 行入场：只动 transform / opacity */
.row-enter-active {
  transition: opacity var(--dur-4) var(--ease-out), transform var(--dur-4) var(--ease-out);
}

.row-enter-from {
  opacity: 0;
  transform: translateY(14px);
}

.row-leave-active {
  transition: opacity var(--dur-2) var(--ease-out);
  position: absolute;
}

.row-leave-to {
  opacity: 0;
}

@media (max-width: 860px) {
  .venue-row {
    grid-template-columns: minmax(0, 1fr);
  }

  .row-cover {
    aspect-ratio: 21 / 9;
  }

  .row-action {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    padding: 14px 20px 18px;
    border-left: 0;
    border-top: 1px solid var(--border-soft);
    min-width: 0;
  }
}

@media (max-width: 640px) {
  .venue-list-wrapper {
    padding: 20px 16px 56px;
  }

  .list-toolbar {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }

  .search-input {
    max-width: none;
  }

  .row-body {
    padding: 16px 18px;
  }

  .row-facts {
    gap: 18px;
  }
}
</style>
