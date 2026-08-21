<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div style="display:flex;align-items:center;gap:12px">
          <el-button size="small" @click="$router.push('/admin/venues')">← 返回场馆列表</el-button>
          <span style="font-size:16px;font-weight:bold">{{ venueName }} — 场地管理</span>
        </div>
      </template>

      <el-button type="primary" @click="openDialog()">新增场地</el-button>
      <el-table :data="list" border stripe v-loading="loading" style="margin-top:12px">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="场地名称" min-width="150" />
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
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openDialog(row)">编辑</el-button>
            <el-popconfirm title="确定删除该场地？已有预约的场地不可删除" @confirm="handleDelete(row.id)">
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
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑场地' : '新增场地'" width="400px">
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
