<template>
  <div class="venue-list-wrapper">
    <div class="page-header">
      <h2>选择场馆</h2>
      <p>选择场馆后查看场地与可预约时段</p>
    </div>

    <div class="list-toolbar">
      <el-input
        v-model="search"
        placeholder="搜索场馆名称"
        clearable
        :prefix-icon="Search"
        class="search-input"
      />
      <span class="result-count">{{ filtered.length }} 个场馆</span>
    </div>

    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="4" animated />
    </div>

    <div v-else-if="filtered.length === 0" class="empty-state">
      <el-empty description="没有找到匹配的场馆" />
    </div>

    <TransitionGroup v-else name="card" tag="div" class="venue-grid" appear>
      <el-card
        v-for="venue in filtered"
        :key="venue.id"
        shadow="never"
        class="venue-card"
        @click="selectVenue(venue)"
      >
        <div class="venue-card-top">
          <span class="venue-icon">
            <el-icon :size="24"><OfficeBuilding /></el-icon>
          </span>
          <div class="venue-main">
            <strong>{{ venue.name }}</strong>
            <span>{{ venue.address || "暂无地址" }}</span>
          </div>
          <el-tag :type="venue.is_active ? 'success' : 'info'" effect="light" round>
            {{ venue.court_count || 0 }} 片场地
          </el-tag>
        </div>

        <div class="venue-details">
          <span class="detail-item">
            <el-icon><Location /></el-icon>
            {{ venue.address || "暂无地址" }}
          </span>
          <span class="detail-item">
            <el-icon><Phone /></el-icon>
            {{ venue.phone || "暂无电话" }}
          </span>
        </div>

        <div class="venue-footer">
          <el-tag :type="venue.is_active ? 'success' : 'info'" effect="plain" round>
            {{ venue.is_active ? "营业中" : "已停用" }}
          </el-tag>
          <el-button type="primary" text @click.stop="selectVenue(venue)">
            查看场地
            <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>
        </div>
      </el-card>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useRouter } from "vue-router"
import { Search, OfficeBuilding, Location, Phone, ArrowRight } from "@element-plus/icons-vue"
import { venueApi } from "@/api/venues"

const router = useRouter()
const venues = ref([])
const loading = ref(true)
const search = ref("")

const filtered = computed(() => {
  if (!search.value) return venues.value
  const q = search.value.toLowerCase()
  return venues.value.filter((v) => v.name.toLowerCase().includes(q))
})

async function fetchVenues() {
  try {
    const res = await venueApi.list({ page_size: 100 })
    venues.value = res.results || []
  } catch (e) {
    console.warn("Fetch venues failed:", e)
  } finally {
    loading.value = false
  }
}

function selectVenue(venue) {
  router.push("/venues/" + venue.id)
}

onMounted(fetchVenues)
</script>

<style scoped>
.venue-list-wrapper {
  width: 100%;
  max-width: 1180px;
  margin: 0 auto;
}

.list-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}

.search-input {
  max-width: 420px;
}

.result-count {
  color: var(--mui-muted);
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
}

.loading-state {
  max-width: 600px;
  margin: 0 auto;
}

.empty-state {
  padding: 60px 0;
}

.venue-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
}

.venue-card {
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}

.venue-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--mui-shadow-lg);
  border-color: #bfdbfe;
}

.venue-card-top {
  display: flex;
  align-items: center;
  gap: 14px;
}

.venue-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 14px;
  color: var(--mui-primary);
  background: var(--mui-primary-soft);
  flex: 0 0 48px;
}

.venue-main {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.venue-main strong {
  color: var(--mui-text);
  font-size: 16px;
  font-weight: 800;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.venue-main span {
  margin-top: 4px;
  color: var(--mui-muted);
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.venue-details {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 18px 0;
  padding: 14px;
  border-radius: 12px;
  background: #f8fafc;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #475569;
  font-size: 13px;
}

.detail-item .el-icon {
  color: var(--mui-primary);
}

.venue-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-top: 14px;
  border-top: 1px solid var(--mui-border-soft);
}

.card-enter-active {
  transition: all 0.4s ease;
}

.card-enter-active:nth-child(1) { transition-delay: 0s; }
.card-enter-active:nth-child(2) { transition-delay: 0.05s; }
.card-enter-active:nth-child(3) { transition-delay: 0.1s; }
.card-enter-active:nth-child(4) { transition-delay: 0.15s; }
.card-enter-active:nth-child(5) { transition-delay: 0.2s; }
.card-enter-active:nth-child(6) { transition-delay: 0.25s; }
.card-enter-from {
  opacity: 0;
  transform: translateY(24px);
}

@media (max-width: 768px) {
  .list-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .search-input {
    max-width: none;
  }

  .venue-grid {
    grid-template-columns: 1fr;
  }
}
</style>
