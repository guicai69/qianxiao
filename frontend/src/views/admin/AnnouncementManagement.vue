<template>
  <div class="page-container">
    <div class="page-header">
      <h2>公告管理</h2>
      <p>发布、置顶与管理场馆公告，会员端首页可见</p>
    </div>

    <el-card class="toolbar-card">
      <div class="page-toolbar">
        <el-input
          v-model="query.keyword"
          placeholder="搜索公告标题"
          clearable
          :prefix-icon="Search"
          style="max-width: 280px"
          @keyup.enter="handleSearch"
        />
        <div>
          <el-button @click="resetQuery">重置</el-button>
          <el-button type="primary" @click="openDialog()">
            <el-icon class="el-icon--left"><Plus /></el-icon>新增公告
          </el-button>
        </div>
      </div>
    </el-card>

    <el-card>
      <el-table :data="list" border stripe v-loading="loading" empty-text="暂无公告">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip />
        <el-table-column label="置顶" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_pinned ? 'danger' : 'info'" effect="light" round size="small">
              {{ row.is_pinned ? '置顶' : '普通' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_published ? 'success' : 'info'" effect="light" round size="small">
              {{ row.is_published ? '已发布' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="170">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
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
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="fetchData"
        class="table-footer"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑公告' : '新增公告'" width="560px">
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
.toolbar-card {
  margin-bottom: 16px;
}

.toolbar-card :deep(.el-card__body) {
  padding: 0;
}
</style>
