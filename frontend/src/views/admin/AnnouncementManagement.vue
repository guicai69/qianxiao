<template>
  <div class="page-container">
    <header class="page-header">
      <h2>公告管理</h2>
      <p>发布、置顶与管理场馆公告，会员端首页可见</p>
    </header>

    <section class="surface panel">
      <div class="page-toolbar">
        <el-input
          v-model="query.keyword"
          placeholder="搜索公告标题"
          clearable
          :prefix-icon="Search"
          class="search-input"
          @keyup.enter="handleSearch"
        />
        <div class="toolbar-actions">
          <el-button @click="resetQuery">重置</el-button>
          <el-button type="primary" @click="openDialog()">
            <el-icon class="el-icon--left"><Plus /></el-icon>新增公告
          </el-button>
        </div>
      </div>

      <el-table :data="list" v-loading="loading">
        <el-table-column prop="id" label="ID" width="70">
          <template #default="{ row }"><span class="mono dim">{{ row.id }}</span></template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="240" show-overflow-tooltip />
        <el-table-column label="置顶" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_pinned ? 'warning' : 'info'" effect="light" round size="small">
              {{ row.is_pinned ? '置顶' : '普通' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_published ? 'success' : 'warning'" effect="light" round size="small">
              {{ row.is_published ? '已发布' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }"><span class="mono dim">{{ formatTime(row.created_at) }}</span></template>
        </el-table-column>
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="togglePin(row)">
              {{ row.is_pinned ? '取消置顶' : '置顶' }}
            </el-button>
            <el-button size="small" @click="togglePublish(row)">
              {{ row.is_published ? '下线' : '发布' }}
            </el-button>
            <el-button size="small" type="primary" @click="openDialog(row)">编辑</el-button>
            <el-popconfirm title="确定删除该公告？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button size="small" type="danger" plain>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>

        <template #empty>
          <div class="empty-state">
            <strong>还没有公告，先写一条</strong>
            <span>发布后会员端首页的公告栏就能看到。</span>
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

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑公告' : '新增公告'" width="min(560px, 92vw)">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入公告标题" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="5"
            placeholder="请输入公告内容"
          />
        </el-form-item>
        <el-form-item label="置顶" prop="is_pinned">
          <el-switch v-model="form.is_pinned" />
        </el-form-item>
        <el-form-item label="发布" prop="is_published">
          <el-switch v-model="form.is_published" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { announcementApi } from '@/api/announcements'

const list = ref([])
const total = ref(0)
const loading = ref(false)
const dialogVisible = ref(false)
const submitLoading = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const formRef = ref(null)

const query = reactive({ page: 1, page_size: 20, keyword: '' })
const form = reactive({ title: '', content: '', is_pinned: false, is_published: true })
const rules = {
  title: [{ required: true, message: '请输入公告标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入公告内容', trigger: 'blur' }],
}

function formatTime(t) {
  return (t || '').slice(0, 19).replace('T', ' ')
}

function resetQuery() {
  query.keyword = ''
  query.page = 1
  fetchData()
}

function handleSearch() {
  query.page = 1
  fetchData()
}

async function fetchData() {
  loading.value = true
  try {
    const params = { page: query.page, page_size: query.page_size }
    if (query.keyword) params.title = query.keyword
    const res = await announcementApi.list(params)
    list.value = res.results || []
    total.value = res.count || 0
  } catch {
    // handled by interceptor
  } finally {
    loading.value = false
  }
}

function openDialog(row) {
  isEdit.value = !!row
  editId.value = row?.id || null
  if (row) {
    form.title = row.title
    form.content = row.content
    form.is_pinned = row.is_pinned
    form.is_published = row.is_published
  } else {
    form.title = ''
    form.content = ''
    form.is_pinned = false
    form.is_published = true
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
        await announcementApi.update(editId.value, { ...form })
        ElMessage.success('已更新')
      } else {
        await announcementApi.create({ ...form })
        ElMessage.success('已创建')
      }
      dialogVisible.value = false
      fetchData()
    } catch {
      // handled by interceptor
    } finally {
      submitLoading.value = false
    }
  })
}

async function togglePublish(row) {
  try {
    await announcementApi.togglePublish(row.id)
    ElMessage.success(row.is_published ? '已下线' : '已发布')
    fetchData()
  } catch {}
}

async function togglePin(row) {
  try {
    await announcementApi.togglePin(row.id)
    ElMessage.success(row.is_pinned ? '已取消置顶' : '已置顶')
    fetchData()
  } catch {}
}

async function handleDelete(id) {
  try {
    await announcementApi.delete(id)
    ElMessage.success('已删除')
    fetchData()
  } catch {}
}

onMounted(fetchData)
</script>

<style scoped>
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

.search-input {
  max-width: 280px;
}

.table-footer :deep(.el-pagination) {
  flex-wrap: wrap;
  row-gap: 8px;
}

@media (max-width: 768px) {
  .panel {
    padding: 14px;
  }

  .search-input {
    max-width: none;
    width: 100%;
  }

  .toolbar-actions {
    width: 100%;
  }

  .toolbar-actions :deep(.el-button) {
    flex: 1 1 auto;
  }
}
</style>
