<template>
  <div class="venue-detail">
    <el-button size="small" @click="$router.push('/venues')" style="margin-bottom:16px">
      ← 返回场馆列表
    </el-button>

    <div v-if="loading" style="text-align:center;padding:40px">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <template v-else-if="venue">
      <el-card class="info-card">
        <h2>{{ venue.name }}</h2>
        <div class="info-item">
          <el-icon><Location /></el-icon>
          <span>{{ venue.address || '暂无地址' }}</span>
        </div>
        <div class="info-item">
          <el-icon><Phone /></el-icon>
          <span>{{ venue.phone || '暂无电话' }}</span>
        </div>
        <p v-if="venue.description" class="desc">{{ venue.description }}</p>
      </el-card>

      <el-row :gutter="20" style="margin-top:20px">
        <el-col :span="12">
          <el-card>
            <template #header><span>场地列表</span></template>
            <div v-if="venue.courts.length === 0" style="color:#909399;text-align:center">暂无场地</div>
            <el-tag v-for="court in venue.courts" :key="court.id" style="margin:4px" size="large">
              {{ court.name }}
            </el-tag>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card>
            <template #header><span>时段与价格</span></template>
            <div v-if="venue.time_slots.length === 0" style="color:#909399;text-align:center">暂无时段</div>
            <el-table v-else :data="venue.time_slots" size="small" stripe>
              <el-table-column prop="display" label="时段" width="110" />
              <el-table-column prop="price" label="价格" width="80">
                <template #default="{ row }">¥{{ row.price }}</template>
              </el-table-column>
              <el-table-column label="操作" width="80">
                <template #default="{ row }">
                  <el-button size="small" type="primary" @click="handleBook(row)">
                    预约
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </template>

    <div v-else style="text-align:center;padding:40px;color:#909399">场馆不存在</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Location, Phone, Loading } from '@element-plus/icons-vue'
import { venueApi } from '@/api/venues'

const route = useRoute()
const venue = ref(null)
const loading = ref(true)

async function fetchVenue() {
  try {
    const res = await venueApi.detail(route.params.id)
    venue.value = res
  } catch {
    ElMessage.error('获取场馆信息失败')
  } finally {
    loading.value = false
  }
}

function handleBook(slot) {
  ElMessage.info(`预约 ${venue.value.name} · ${slot.display} · ¥${slot.price} （预约功能将在后续版本开放）`)
}

onMounted(fetchVenue)
</script>

<style scoped>
.venue-detail { max-width: 1000px; margin: 0 auto; padding: 20px; }
.info-card { margin-bottom: 0; }
.info-card h2 { margin: 0 0 12px; color: #303133; }
.info-item { display: flex; align-items: center; gap: 6px; color: #606266; margin-bottom: 6px; }
.desc { color: #909399; margin-top: 8px; font-size: 13px; }
</style>
