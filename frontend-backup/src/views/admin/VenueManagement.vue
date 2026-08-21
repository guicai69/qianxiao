<template>
  <div class="page-container">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :model="query" inline>
        <el-form-item label="场馆名称">
          <el-input v-model="query.name" placeholder="搜索场馆名称" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.is_active" clearable placeholder="全部">
            <el-option label="启用" :value="true" />
            <el-option label="停用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">搜索</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <el-button type="primary" @click="openDialog()">新增场馆</el-button>
      <el-table :data="list" border stripe v-loading="loading" style="margin-top:12px">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="场馆名称" min-width="150" />
        <el-table-column prop="address" label="地址" min-width="200" show-overflow-tooltip />
        <el-table-column prop="phone" label="联系电话" width="130" />
        <el-table-column prop="court_count" label="场地数" width="80" align="center" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="110">
          <template #default="{ row }">{{ row.created_at?.slice(0, 10) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="$router.push(`/admin/venues/${row.id}/courts`)">
              场地管理
            </el-button>
            <el-button size="small" @click="$router.push(`/admin/venues/${row.id}/timeslots`)">
              时段管理
            </el-button>
            <el-button size="small" @click="openDialog(row)">编辑</el-button>
            <el-popconfirm title="确定删除该场馆？" @confirm="handleDelete(row.id)">
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
        style="margin-top:16px"
      />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑场馆' : '新增场馆'" width="500px">
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { venueApi } from '@/api/venues'

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
  name: '',
  is_active: null,
})

const form = reactive({
  name: '',
  address: '',
  phone: '',
  description: '',
  is_active: true,
})

const rules = {
  name: [{ required: true, message: '请输入场馆名称', trigger: 'blur' }],
}

function resetQuery() {
  query.name = ''
  query.is_active = null
  query.page = 1
  fetchData()
}

async function fetchData() {
  loading.value = true
  try {
    const res = await venueApi.list(query)
    list.value = res.results
    total.value = res.count
  } finally {
    loading.value = false
  }
}

function openDialog(row) {
  editId.value = row?.id || null
  isEdit.value = !!row
  if (row) {
    form.name = row.name
    form.address = row.address
    form.phone = row.phone
    form.description = row.description || ''
    form.is_active = row.is_active
  } else {
    form.name = ''
    form.address = ''
    form.phone = ''
    form.description = ''
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
        await venueApi.update(editId.value, form)
        ElMessage.success('编辑成功')
      } else {
        await venueApi.create(form)
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
    await venueApi.delete(id)
    ElMessage.success('删除成功')
    fetchData()
  } catch { /* handled by interceptor */ }
}

onMounted(fetchData)
</script>
