<template>
  <div class="page-container">
    <header class="page-header">
      <h2>优惠券管理</h2>
      <p>发行满减券，控制上下架与发行量</p>
    </header>

    <section class="surface panel">
      <div class="page-toolbar">
        <div class="toolbar-actions">
          <el-button type="primary" @click="openDialog()">
            <el-icon class="el-icon--left"><Plus /></el-icon>发行优惠券
          </el-button>
        </div>
      </div>

      <el-table :data="list" v-loading="loading">
        <el-table-column prop="id" label="ID" width="60">
          <template #default="{ row }"><span class="mono dim">{{ row.id }}</span></template>
        </el-table-column>
        <el-table-column prop="name" label="名称" min-width="160" show-overflow-tooltip />
        <el-table-column label="面额" width="90">
          <template #default="{ row }"><span class="mono accent">¥{{ row.amount }}</span></template>
        </el-table-column>
        <el-table-column label="满减阈值" width="110">
          <template #default="{ row }">满 ¥{{ row.min_amount }}</template>
        </el-table-column>
        <el-table-column label="发行" width="90" align="center">
          <template #default="{ row }">{{ row.claimed }}/{{ row.total }}</template>
        </el-table-column>
        <el-table-column label="有效期至" width="170">
          <template #default="{ row }"><span class="mono dim">{{ formatTime(row.expires_at) }}</span></template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_expired" type="danger" effect="light" round size="small">已过期</el-tag>
            <el-tag v-else :type="row.is_active ? 'success' : 'info'" effect="light" round size="small">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="toggleActive(row)">{{ row.is_active ? '下架' : '上架' }}</el-button>
            <el-button size="small" type="primary" @click="openDialog(row)">编辑</el-button>
            <el-popconfirm title="确定删除该优惠券？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button size="small" type="danger" plain>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
        <template #empty>
          <div class="empty-state"><strong>还没有优惠券</strong><span>点击「发行优惠券」创建第一张。</span></div>
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

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑优惠券' : '发行优惠券'" width="min(520px, 92vw)">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="如：新会员立减券" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="面额" prop="amount">
          <el-input-number v-model="form.amount" :min="0.01" :step="5" :precision="2" style="width: 180px" />
        </el-form-item>
        <el-form-item label="满减阈值" prop="min_amount">
          <el-input-number v-model="form.min_amount" :min="0" :step="10" :precision="2" style="width: 180px" />
        </el-form-item>
        <el-form-item label="发行量" prop="total">
          <el-input-number v-model="form.total" :min="1" :step="10" style="width: 180px" />
        </el-form-item>
        <el-form-item label="有效期至" prop="expires_at">
          <el-date-picker v-model="form.expires_at" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="有效期至" style="width: 100%" />
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
import { Plus } from '@element-plus/icons-vue'
import { couponApi } from '@/api/coupons'

const list = ref([])
const total = ref(0)
const loading = ref(false)
const dialogVisible = ref(false)
const submitLoading = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const formRef = ref(null)

const query = reactive({ page: 1, page_size: 20 })
const form = reactive({ name: '', amount: 10, min_amount: 0, total: 100, expires_at: '' })

const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  amount: [{ required: true, message: '请输入面额', trigger: 'blur' }],
  total: [{ required: true, message: '请输入发行量', trigger: 'blur' }],
  expires_at: [{ required: true, message: '请选择有效期', trigger: 'change' }],
}

function formatTime(t) { return (t || '').slice(0, 19).replace('T', ' ') }

async function fetchData() {
  loading.value = true
  try {
    const res = await couponApi.list({ page: query.page, page_size: query.page_size })
    list.value = res.results || []
    total.value = res.count || 0
  } catch {} finally { loading.value = false }
}

function openDialog(row) {
  isEdit.value = !!row
  editId.value = row?.id || null
  if (row) {
    form.name = row.name
    form.amount = Number(row.amount)
    form.min_amount = Number(row.min_amount)
    form.total = row.total
    form.expires_at = row.expires_at ? row.expires_at.slice(0, 19) : ''
  } else {
    Object.assign(form, { name: '', amount: 10, min_amount: 0, total: 100, expires_at: '' })
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
        await couponApi.update(editId.value, { ...form })
        ElMessage.success('已更新')
      } else {
        await couponApi.create({ ...form })
        ElMessage.success('已发行')
      }
      dialogVisible.value = false
      fetchData()
    } catch {} finally { submitLoading.value = false }
  })
}

async function toggleActive(row) {
  try { await couponApi.toggleActive(row.id); ElMessage.success(row.is_active ? '已下架' : '已上架'); fetchData() } catch {}
}

async function handleDelete(id) {
  try { await couponApi.delete(id); ElMessage.success('已删除'); fetchData() } catch {}
}

onMounted(fetchData)
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
