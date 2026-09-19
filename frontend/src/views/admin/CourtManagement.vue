<template>
  <div class="page-container">
    <header class="page-header">
      <el-button link class="back-link" @click="$router.push('/admin/venues')">← 返回场馆列表</el-button>
      <h2>场地管理</h2>
      <p>{{ venueName || '当前场馆' }} · 共 {{ total }} 片场地</p>
    </header>

    <section class="surface panel">
      <div class="page-toolbar">
        <p class="toolbar-hint">已有预约的场地不能删除，停用后会员端不再可选</p>
        <div class="toolbar-actions">
          <el-button type="primary" @click="openDialog()">
            <el-icon class="el-icon--left"><Plus /></el-icon>新增场地
          </el-button>
        </div>
      </div>

      <el-table :data="list" v-loading="loading">
        <el-table-column prop="id" label="ID" width="60">
          <template #default="{ row }"><span class="mono dim">{{ row.id }}</span></template>
        </el-table-column>
        <el-table-column prop="name" label="场地名称" width="240" show-overflow-tooltip />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" effect="light" round size="small">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="112">
          <template #default="{ row }"><span class="mono dim">{{ row.created_at?.slice(0, 10) }}</span></template>
        </el-table-column>
        <el-table-column label="操作" width="190" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openDialog(row)">编辑</el-button>
            <el-popconfirm title="确定删除该场地？已有预约的场地不可删除" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button size="small" type="danger" plain>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>

        <template #empty>
          <div class="empty-state">
            <strong>这座场馆还没有场地</strong>
            <span>先新增第一片场地，会员才能选到它。</span>
          </div>
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

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑场地' : '新增场地'" width="min(420px, 92vw)">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="场地名称" prop="name">
          <el-input v-model="form.name" placeholder="如：1号场" />
        </el-form-item>
        <el-form-item label="启用" prop="is_active">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { courtApi, venueApi } from '@/api/venues'

const route = useRoute()
const venueId = Number(route.params.id)
const venueName = ref('')
const list = ref([])
const total = ref(0)
const loading = ref(false)
const dialogVisible = ref(false)
const submitLoading = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const formRef = ref(null)

const query = reactive({
  page: 1,
  page_size: 20,
  venue: venueId,
})

const form = reactive({
  venue: venueId,
  name: '',
  is_active: true,
})

const rules = {
  name: [{ required: true, message: '请输入场地名称', trigger: 'blur' }],
}

async function fetchData() {
  loading.value = true
  try {
    const res = await courtApi.list(query)
    list.value = res.results
    total.value = res.count
  } finally {
    loading.value = false
  }
}

async function fetchVenueName() {
  try {
    const res = await venueApi.detail(venueId)
    venueName.value = res.data?.name || ''
  } catch { /* ignore */ }
}

function openDialog(row) {
  editId.value = row?.id || null
  isEdit.value = !!row
  if (row) {
    form.name = row.name
    form.is_active = row.is_active
  } else {
    form.name = ''
    form.is_active = true
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
        await courtApi.update(editId.value, { name: form.name, is_active: form.is_active })
        ElMessage.success('编辑成功')
      } else {
        await courtApi.create(form)
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      fetchData()
    } finally {
      submitLoading.value = false
    }
  })
}

async function handleDelete(id) {
  try {
    await courtApi.delete(id)
    ElMessage.success('删除成功')
    fetchData()
  } catch { /* handled by interceptor */ }
}

onMounted(() => {
  fetchVenueName()
  fetchData()
})
</script>

<style scoped>
.back-link {
  margin-bottom: 10px;
  padding: 0;
  height: auto;
  color: var(--ink-3);
  font-weight: 600;
}

.back-link:hover {
  color: var(--accent);
}

.panel {
  padding: 20px;
}

.panel :deep(.page-toolbar) {
  padding-bottom: 14px;
  border-bottom: 1px solid var(--border-soft);
}

/* 固定列要有不透明底色，否则横向滚动时下面的单元格会透出来 */
.panel :deep(.el-table) {
  --el-table-tr-bg-color: var(--surface);
}

/* 表格空态要占满整宽，不能跟着表格布局计算塌成窄条 */
.panel :deep(.el-table__empty-block) {
  width: 100% !important;
}

.panel :deep(.el-table__empty-text) {
  width: 100%;
  line-height: normal;
}

.toolbar-hint {
  margin: 0;
  color: var(--ink-3);
  font-size: var(--fs-13);
}

.table-footer :deep(.el-pagination) {
  flex-wrap: wrap;
  row-gap: 8px;
}

@media (max-width: 768px) {
  .panel {
    padding: 14px;
  }

  .toolbar-actions {
    width: 100%;
  }

  .toolbar-actions :deep(.el-button) {
    flex: 1 1 auto;
  }
}
</style>
