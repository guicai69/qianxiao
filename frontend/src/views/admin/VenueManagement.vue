<template>
  <div class="page-container">
    <header class="page-header">
      <h2>场馆管理</h2>
      <p>维护球馆信息与上下线状态，进入单个场馆可继续管理场地与时段</p>
    </header>

    <section class="surface panel">
      <div class="page-toolbar">
        <el-form :model="query" inline class="filter-form">
          <el-form-item label="场馆名称">
            <el-input v-model="query.name" placeholder="搜索场馆名称" clearable class="w-220" />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="query.is_active" clearable placeholder="全部" class="w-120">
              <el-option label="启用" :value="true" />
              <el-option label="停用" :value="false" />
            </el-select>
          </el-form-item>
          <el-form-item class="filter-actions">
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetQuery">重置</el-button>
          </el-form-item>
        </el-form>

        <div class="toolbar-actions">
          <el-button type="primary" @click="openDialog()">
            <el-icon class="el-icon--left"><Plus /></el-icon>新增场馆
          </el-button>
        </div>
      </div>

      <el-table :data="list" v-loading="loading">
        <el-table-column prop="id" label="ID" width="60">
          <template #default="{ row }"><span class="mono dim">{{ row.id }}</span></template>
        </el-table-column>
        <el-table-column prop="name" label="场馆名称" min-width="150" />
        <el-table-column prop="address" label="地址" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">{{ row.address || '地址待补充' }}</template>
        </el-table-column>
        <el-table-column prop="phone" label="联系电话" width="132">
          <template #default="{ row }"><span class="mono">{{ row.phone || '—' }}</span></template>
        </el-table-column>
        <el-table-column prop="court_count" label="场地数" width="92" align="right">
          <template #default="{ row }"><span class="mono">{{ row.court_count }}</span></template>
        </el-table-column>
        <el-table-column label="状态" width="88">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" effect="light" round size="small">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="112">
          <template #default="{ row }"><span class="mono dim">{{ row.created_at?.slice(0, 10) }}</span></template>
        </el-table-column>
        <el-table-column label="操作" width="272" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" plain @click="$router.push(`/admin/venues/${row.id}/courts`)">场地</el-button>
            <el-button size="small" @click="$router.push(`/admin/venues/${row.id}/timeslots`)">时段</el-button>
            <el-button size="small" @click="openDialog(row)">编辑</el-button>
            <el-popconfirm title="确定删除该场馆？" @confirm="handleDelete(row.id)">
              <template #reference><el-button size="small" type="danger" plain>删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>

        <template #empty>
          <div class="empty-state">
            <strong>还没有场馆，先新建一个</strong>
            <span>场馆建好后，再往里添加场地与开放时段。</span>
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

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑场馆' : '新增场馆'" width="min(500px, 92vw)">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="场馆名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入场馆名称" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="form.address" placeholder="请输入地址" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="场馆描述" />
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
import { ref, reactive, onMounted } from "vue"
import { ElMessage } from "element-plus"
import { Plus } from "@element-plus/icons-vue"
import { venueApi } from "@/api/venues"

const list = ref([])
const total = ref(0)
const loading = ref(false)
const dialogVisible = ref(false)
const submitLoading = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const formRef = ref(null)

const query = reactive({ page: 1, page_size: 20, name: "", is_active: null })

const form = reactive({ name: "", address: "", phone: "", description: "", is_active: true })
const rules = { name: [{ required: true, message: "请输入场馆名称", trigger: "blur" }] }

function resetQuery() { query.name = ""; query.is_active = null; query.page = 1; fetchData() }

function handleSearch() {
  query.page = 1
  fetchData()
}

async function fetchData() {
  loading.value = true
  try {
    const params = { page: query.page, page_size: query.page_size }
    if (query.name) params.name = query.name
    if (query.is_active !== null && query.is_active !== '') params.is_active = query.is_active
    const res = await venueApi.list(params)
    list.value = res.results
    total.value = res.count
  }
  finally { loading.value = false }
}

function openDialog(row) {
  editId.value = row?.id || null; isEdit.value = !!row
  if (row) { form.name = row.name; form.address = row.address; form.phone = row.phone; form.description = row.description || ""; form.is_active = row.is_active }
  else { form.name = ""; form.address = ""; form.phone = ""; form.description = ""; form.is_active = true }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return; submitLoading.value = true
    try {
      if (isEdit.value) { await venueApi.update(editId.value, form); ElMessage.success("编辑成功") }
      else { await venueApi.create(form); ElMessage.success("新增成功") }
      dialogVisible.value = false; fetchData()
    } finally { submitLoading.value = false }
  })
}

async function handleDelete(id) {
  try { await venueApi.delete(id); ElMessage.success("删除成功"); fetchData() } catch {}
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

.filter-form {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  row-gap: 10px;
}

.filter-form :deep(.el-form-item) {
  margin: 0 14px 0 0;
}

.filter-form :deep(.el-form-item__label) {
  color: var(--ink-3);
  font-weight: 600;
}

.filter-form :deep(.filter-actions .el-form-item__content) {
  gap: 8px;
}

.w-220 { width: 220px; }
.w-120 { width: 120px; }

.table-footer :deep(.el-pagination) {
  flex-wrap: wrap;
  row-gap: 8px;
}

@media (max-width: 768px) {
  .panel {
    padding: 14px;
  }

  .filter-form :deep(.el-form-item) {
    flex: 1 1 100%;
    margin-right: 0;
  }

  .filter-form :deep(.el-form-item__content) {
    flex: 1 1 auto;
    min-width: 0;
  }

  .filter-form :deep(.el-input),
  .filter-form :deep(.el-select) {
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
