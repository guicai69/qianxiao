<template>
  <div class="page-container">
    <header class="page-header">
      <h2>用户管理</h2>
      <p>管理会员、前台与管理员账号，可拉黑、改角色与调整会员等级</p>
    </header>

    <section class="surface panel">
      <div class="page-toolbar">
        <el-form :model="query" inline class="filter-form">
          <el-form-item label="手机号">
            <el-input v-model="query.phone" placeholder="搜索手机号" clearable class="w-200" />
          </el-form-item>
          <el-form-item label="角色">
            <el-select v-model="query.role" clearable placeholder="全部" class="w-120">
              <el-option label="管理员" value="admin" />
              <el-option label="前台" value="reception" />
              <el-option label="会员" value="member" />
            </el-select>
          </el-form-item>
          <el-form-item class="filter-actions">
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetQuery">重置</el-button>
          </el-form-item>
        </el-form>

        <div class="toolbar-actions">
          <el-button type="primary" @click="openCreate">
            <el-icon class="el-icon--left"><Plus /></el-icon>新增用户
          </el-button>
        </div>
      </div>

      <el-tabs v-model="activeTab" @tab-change="handleTabChange" class="list-tabs">
        <el-tab-pane label="全部用户" name="all" />
        <el-tab-pane label="黑名单" name="blacklist" />
      </el-tabs>

      <el-table :data="displayList" v-loading="loading">
        <el-table-column prop="id" label="ID" width="56">
          <template #default="{ row }"><span class="mono dim">{{ row.id }}</span></template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" width="132">
          <template #default="{ row }"><span class="mono">{{ row.phone }}</span></template>
        </el-table-column>
        <el-table-column prop="nickname" label="昵称" min-width="130">
          <template #default="{ row }">{{ row.nickname || '未设置昵称' }}</template>
        </el-table-column>
        <el-table-column prop="role" label="角色" width="92">
          <template #default="{ row }">
            <el-tag :type="roleTag(row.role)" effect="light" round size="small">{{ roleLabel(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="level" label="等级" width="104">
          <template #default="{ row }">{{ levelLabel(row.level) }}</template>
        </el-table-column>
        <el-table-column prop="balance" label="余额" width="104" align="right">
          <template #default="{ row }"><span class="mono amount">¥{{ row.balance ?? 0 }}</span></template>
        </el-table-column>
        <el-table-column prop="is_blacklisted" label="状态" width="88">
          <template #default="{ row }">
            <el-tag :type="row.is_blacklisted ? 'danger' : 'success'" effect="light" round size="small">
              {{ row.is_blacklisted ? '已拉黑' : '正常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="date_joined" label="注册时间" width="112">
          <template #default="{ row }"><span class="mono dim">{{ row.date_joined?.slice(0, 10) }}</span></template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-popconfirm v-if="!row.is_blacklisted" title="确定拉黑？" @confirm="blacklistUser(row)">
              <template #reference><el-button size="small" type="warning" plain>拉黑</el-button></template>
            </el-popconfirm>
            <el-button v-else size="small" type="success" plain @click="unblacklistUser(row)">取消拉黑</el-button>
            <el-popconfirm title="确定删除？" @confirm="deleteUser(row)">
              <template #reference><el-button size="small" type="danger" plain>删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>

        <template #empty>
          <div class="empty-state">
            <template v-if="activeTab === 'blacklist'">
              <strong>黑名单是空的</strong>
              <span>被拉黑的用户会出现在这里，可以随时取消拉黑。</span>
            </template>
            <template v-else>
              <strong>没有符合条件的用户</strong>
              <span>换个手机号或角色，或点重置看全部用户。</span>
            </template>
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

    <el-dialog v-model="dialog.visible" :title="dialog.isCreate ? '新增用户' : '编辑用户'" width="min(460px, 92vw)">
      <el-form ref="dialogRef" :model="dialog.form" :rules="dialog.rules" label-width="80px">
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="dialog.form.phone" :disabled="!dialog.isCreate" />
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="dialog.form.nickname" />
        </el-form-item>
        <el-form-item v-if="dialog.isCreate" label="密码" prop="password">
          <el-input v-model="dialog.form.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="dialog.form.role">
            <el-option label="管理员" value="admin" />
            <el-option label="前台" value="reception" />
            <el-option label="会员" value="member" />
          </el-select>
        </el-form-item>
        <el-form-item label="会员等级" prop="level">
          <el-select v-model="dialog.form.level">
            <el-option label="普通会员" value="normal" />
            <el-option label="银卡会员（95折）" value="silver" />
            <el-option label="金卡会员" value="gold" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="dialog.saving" @click="submitDialog">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from "vue"
import { ElMessage } from "element-plus"
import { Plus } from "@element-plus/icons-vue"
import api from "@/api"

const list = ref([])
const total = ref(0)
const loading = ref(false)
const activeTab = ref("all")
const query = reactive({ page: 1, page_size: 20, phone: "", role: "" })
const dialogRef = ref(null)

const displayList = computed(() => list.value)

const dialog = reactive({
  visible: false, isCreate: true, saving: false,
  editingId: null,
  form: { phone: "", nickname: "", password: "", role: "member", level: "normal" },
  rules: {
    phone: [
      { required: true, message: "请输入手机号", trigger: "blur" },
      { pattern: /^1\d{10}$/, message: "手机号格式不正确", trigger: "blur" },
    ],
    password: [{ required: true, message: "请输入密码", trigger: "blur" }, { min: 6, message: "密码至少6位", trigger: "blur" }],
    role: [{ required: true, message: "请选择角色", trigger: "change" }],
  },
})

const roleTag = (r) => ({ admin: "primary", reception: "warning", member: "info" }[r] || "info")
const roleLabel = (r) => ({ admin: "管理员", reception: "前台", member: "会员" }[r])
const levelLabel = (l) => ({ normal: "普通会员", silver: "银卡会员", gold: "金卡会员" }[l] || l)

const fetchData = async () => {
  loading.value = true
  try {
    const params = { page: query.page, page_size: query.page_size }
    if (query.phone) params.phone = query.phone
    if (query.role) params.role = query.role
    if (activeTab.value === "blacklist") params.is_blacklisted = true
    const res = await api.get("users/", params)
    list.value = res.results; total.value = res.count
  } catch {} finally { loading.value = false }
}

const handleSearch = () => {
  query.page = 1
  fetchData()
}

const handleTabChange = () => {
  query.page = 1
  fetchData()
}

const resetQuery = () => {
  query.page = 1; query.phone = ""; query.role = ""
  fetchData()
}

const openCreate = () => {
  dialog.isCreate = true; dialog.editingId = null
  dialog.form = { phone: "", nickname: "", password: "", role: "member", level: "normal" }
  dialog.visible = true
}

const openEdit = (row) => {
  dialog.isCreate = false; dialog.editingId = row.id
  dialog.form = { phone: row.phone, nickname: row.nickname || "", password: "", role: row.role, level: row.level }
  dialog.visible = true
}

const submitDialog = async () => {
  if (!dialogRef.value) return
  await dialogRef.value.validate(async (valid) => {
    if (!valid) return; dialog.saving = true
    try {
      if (dialog.isCreate) { await api.post("users/", { ...dialog.form }); ElMessage.success("创建成功") }
      else { await api.patch(`users/${dialog.editingId}/`, { nickname: dialog.form.nickname, role: dialog.form.role, level: dialog.form.level }); ElMessage.success("已更新") }
      dialog.visible = false; fetchData()
    } catch {} finally { dialog.saving = false }
  })
}

const blacklistUser = async (row) => {
  try { await api.post(`users/${row.id}/blacklist/`); ElMessage.success("已拉黑"); fetchData() } catch {}
}

const unblacklistUser = async (row) => {
  try { await api.post(`users/${row.id}/unblacklist/`); ElMessage.success("取消拉黑"); fetchData() } catch {}
}

const deleteUser = async (row) => {
  try { await api.delete(`users/${row.id}/`); ElMessage.success("已删除"); fetchData() } catch {}
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

.w-200 { width: 200px; }
.w-120 { width: 120px; }

.list-tabs {
  margin-top: 4px;
}

.list-tabs :deep(.el-tabs__header) {
  margin-bottom: 8px;
}

.amount {
  color: var(--ink-1);
  font-weight: 700;
}

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
