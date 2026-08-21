<template>
  <div class="venue-list">
    <h2>选择场馆</h2>
    <p class="subtitle">请选择您要预约的场馆</p>

    <div v-if="loading" style="text-align:center;padding:40px">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <div v-else-if="venues.length === 0" style="text-align:center;padding:40px;color:#909399">
      暂无可用场馆
    </div>

    <el-row v-else :gutter="20">
      <el-col v-for="venue in venues" :key="venue.id" :xs="24" :sm="12" :md="8" style="margin-bottom:20px">
        <el-card shadow="hover" class="venue-card" @click="selectVenue(venue)">
          <div class="venue-name">{{ venue.name }}</div>
          <div class="venue-info">
            <el-icon><Location /></el-icon>
            <span>{{ venue.address || '暂无地址' }}</span>
          </div>
          <div class="venue-info">
            <el-icon><Phone /></el-icon>
            <span>{{ venue.phone || '暂无电话' }}</span>
          </div>
          <div class="venue-meta">
            <el-tag size="small" type="info">{{ venue.court_count }} 片场地</el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Location, Phone, Loading } from '@element-plus/icons-vue'
import { venueApi } from '@/api/venues'

const router = useRouter()
const venues = ref([])
const loading = ref(true)

async function fetchVenues() {
  try {
    const res = await venueApi.list({ page_size: 100 })
    venues.value = res.results || []
  } catch {
    ElMessage.error('获取场馆列表失败')
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
.venue-list { max-width: 1000px; margin: 0 auto; padding: 20px; }
.venue-list h2 { text-align: center; margin-bottom: 4px; }
.subtitle { text-align: center; color: #909399; margin-bottom: 24px; }
.venue-card { cursor: pointer; transition: transform .2s; }
.venue-card:hover { transform: translateY(-4px); }
.venue-name { font-size: 18px; font-weight: bold; margin-bottom: 12px; color: #303133; }
.venue-info { display: flex; align-items: center; gap: 6px; color: #606266; font-size: 14px; margin-bottom: 6px; }
.venue-meta { margin-top: 12px; }
</style>
