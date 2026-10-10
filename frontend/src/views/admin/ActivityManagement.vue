<template>
  <div class="page-container">
    <header class="page-header">
      <h2>活动管理</h2>
      <p>发布比赛、培训、教练课，查看报名名单并核销到场</p>
    </header>

    <section class="surface panel">
      <div class="page-toolbar">
        <el-select v-model="query.type" placeholder="全部类型" clearable style="width: 140px" @change="handleSearch">
          <el-option label="比赛" value="match" />
          <el-option label="培训" value="training" />
          <el-option label="教练课" value="coach" />
        </el-select>
        <div class="toolbar-actions">
          <el-button type="primary" @click="openDialog()">
            <el-icon class="el-icon--left"><Plus /></el-icon>新增活动
          </el-button>
        </div>
      </div>

      <el-table :data="list" v-loading="loading">
        <el-table-column prop="id" label="ID" width="60">
          <template #default="{ row }"><span class="mono dim">{{ row.id }}</span></template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
        <el-table-column label="类型" width="90">
          <template #default="{ row }">
            <el-tag size="small" round effect="light">{{ typeLabel(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="venue_name" label="场馆" min-width="120" />
        <el-table-column label="时间" min-width="200">
          <template #default="{ row }">
            <span class="mono dim">{{ formatTime(row.start_at) }} ~ {{ formatTime(row.end_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="名额" width="90" align="center">
          <template #default="{ row }">{{ row.registered }}/{{ row.capacity }}</template>
        </el-table-column>
        <el-table-column label="价格" width="90">
          <template #default="{ row }"><span class="mono">¥{{ row.price }}</span></template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" effect="light" round size="small">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openRoster(row)">名单</el-button>
            <el-button size="small" @click="toggleActive(row)">{{ row.is_active ? '下架' : '上架' }}</el-button>
            <el-button size="small" type="primary" @click="openDialog(row)">编辑</el-button>
            <el-popconfirm title="确定删除该活动？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button size="small" type="danger" plain>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
        <template #empty>
          <div class="empty-state"><strong>还没有活动</strong><span>点击「新增活动」发布第一条。</span></div>
        </template>
      </el-table>

      <div class="table-footer">
        <el-pagination
          v-model:current-page="query.page"
          v-model:page-size="query.page_size"
          :total="total"
          :pager-count="5"
          layout="total, prev, pager, next"
          @current-change="fetchData"
        />
      </div>
    </section>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑活动' : '新增活动'" width="min(640px, 92vw)">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入活动标题" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="类型" prop="type">
          <el-select v-model="form.type" style="width: 100%">
            <el-option label="比赛" value="match" />
            <el-option label="培训" value="training" />
            <el-option label="教练课" value="coach" />
          </el-select>
        </el-form-item>
        <el-form-item label="场馆" prop="venue">
          <el-select v-model="form.venue" style="width: 100%" placeholder="选择场馆">
            <el-option v-for="v in venues" :key="v.id" :label="v.name" :value="v.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="说明" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="活动说明（可选）" />
        </el-form-item>
        <el-form-item label="开始时间" prop="start_at">
          <el-date-picker v-model="form.start_at" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="开始时间" style="width: 100%" />
        </el-form-item>
        <el-form-item label="结束时间" prop="end_at">
          <el-date-picker v-model="form.end_at" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="结束时间" style="width: 100%" />
        </el-form-item>
        <el-form-item label="报名截止" prop="deadline">
          <el-date-picker v-model="form.deadline" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="报名截止" style="width: 100%" />
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input-number v-model="form.price" :min="0" :step="10" :precision="2" style="width: 180px" />
        </el-form-item>
        <el-form-item label="名额" prop="capacity">
          <el-input-number v-model="form.capacity" :min="1" :step="1" style="width: 180px" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="rosterVisible" :title="`报名名单 · ${currentTitle}`" width="min(560px, 92vw)">
      <el-table :data="roster" v-loading="rosterLoading" empty-text="暂无报名">
        <el-table-column label="用户" min-width="140">
          <template #default="{ row }">{{ row.user_nickname || row.user_phone }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="{ registered: 'primary', attended: 'success', cancelled: 'info' }[row.status]" size="small" round effect="light">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="报名时间" width="170">
          <template #default="{ row }"><span class="mono dim">{{ formatTime(row.created_at) }}</span></template>
        </el-table-column>
        <el-table-column label="操作" width="90" align="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'registered'" size="small" type="success" @click="attend(row)">签到</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { activityApi } from '@/api/activities'
import { venueApi } from '@/api/venues'

const list = ref([])
const total = ref(0)
const loading = ref(false)
const venues = ref([])
const dialogVisible = ref(false)
const submitLoading = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const formRef = ref(null)

const rosterVisible = ref(false)
const rosterLoading = ref(false)
const roster = ref([])
const currentTitle = ref('')
const currentActivityId = ref(null)

const query = reactive({ page: 1, page_size: 20, type: '' })
const form = reactive({ title: '', type: 'match', venue: null, description: '', start_at: '', end_at: '', deadline: '', price: 0, capacity: 10 })

const typeLabel = (t) => ({ match: '比赛', training: '培训', coach: '教练课' }[t] || t)
const statusLabel = (s) => ({ registered: '已报名', attended: '已到场', cancelled: '已取消' }[s] || s)

const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  venue: [{ required: true, message: '请选择场馆', trigger: 'change' }],
  start_at: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  end_at: [{ required: true, message: '请选择结束时间', trigger: 'change' }],
  deadline: [{ required: true, message: '请选择报名截止', trigger: 'change' }],
}

function formatTime(t) { return (t || '').slice(0, 19).replace('T', ' ') }

function handleSearch() { query.page = 1; fetchData() }

async function fetchVenues() {
  try { const r = await venueApi.list({ page_size: 100 }); venues.value = r.results || [] } catch {}
}

async function fetchData() {
  loading.value = true
  try {
    const params = { page: query.page, page_size: query.page_size }
    if (query.type) params.type = query.type
    const res = await activityApi.list(params)
    list.value = res.results || []
    total.value = res.count || 0
  } catch {} finally { loading.value = false }
}

function openDialog(row) {
  isEdit.value = !!row
  editId.value = row?.id || null
  if (row) {
    form.title = row.title
    form.type = row.type
    form.venue = row.venue
    form.description = row.description
    form.start_at = row.start_at ? row.start_at.slice(0, 19) : ''
    form.end_at = row.end_at ? row.end_at.slice(0, 19) : ''
    form.deadline = row.deadline ? row.deadline.slice(0, 19) : ''
    form.price = Number(row.price)
    form.capacity = row.capacity
  } else {
    Object.assign(form, { title: '', type: 'match', venue: null, description: '', start_at: '', end_at: '', deadline: '', price: 0, capacity: 10 })
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    try {
      if (isEdit.value) {
        await activityApi.update(editId.value, { ...form })
        ElMessage.success('已更新')
      } else {
        await activityApi.create({ ...form })
        ElMessage.success('已创建')
      }
      dialogVisible.value = false
      fetchData()
    } catch {} finally { submitLoading.value = false }
  })
}

async function toggleActive(row) {
  try { await activityApi.toggleActive(row.id); ElMessage.success(row.is_active ? '已下架' : '已上架'); fetchData() } catch {}
}

async function handleDelete(id) {
  try { await activityApi.delete(id); ElMessage.success('已删除'); fetchData() } catch {}
}

async function openRoster(row) {
  currentTitle.value = row.title
  currentActivityId.value = row.id
  rosterVisible.value = true
  rosterLoading.value = true
  try {
    const res = await activityApi.registrations(row.id)
    roster.value = res.data || []
  } catch {} finally { rosterLoading.value = false }
}

async function attend(reg) {
  try {
    await activityApi.attend(currentActivityId.value, reg.id)
    ElMessage.success('签到成功')
    const res = await activityApi.registrations(currentActivityId.value)
    roster.value = res.data || []
  } catch {}
}

onMounted(() => { fetchVenues(); fetchData() })
</script>

<style scoped>
.panel {
  padding: 20px;
}

.panel :deep(.el-table) {
  --el-table-tr-bg-color: var(--surface);
}

.panel :deep(.el-table__empty-block) {
  width: 100% !important;
}

.table-footer :deep(.el-pagination) {
  flex-wrap: wrap;
  row-gap: 8px;
}

@media (max-width: 768px) {
  .panel {
    padding: 14px;
  }
}
</style>
