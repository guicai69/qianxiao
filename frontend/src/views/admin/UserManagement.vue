<template>
  <div class="user-management">
    <el-card class="search-card">
      <el-form :model="query" inline>
        <el-form-item label="手机号">
          <el-input v-model="query.phone" placeholder="搜索手机号" clearable />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="query.role" clearable placeholder="全部">
            <el-option label="管理员" value="admin" />
            <el-option label="前台" value="reception" />
            <el-option label="会员" value="member" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-tabs v-model="activeTab" @tab-change="handleTabChange" style="margin-bottom:12px">
      <el-tab-pane label="全部用户" name="all" />
      <el-tab-pane label="黑名单" name="blacklist" />
    </el-tabs>

    <el-card>
      <el-button type="primary" @click="openCreate">新增用户</el-button>
      <el-table :data="displayList" border stripe v-loading="loading" style="margin-top:12px">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="nickname" label="昵称" width="120" />
        <el-table-column prop="role" label="角色" width="90">
          <template #default="{ row }">
            <el-tag :type="roleTag(row.role)" size="small">{{ roleLabel(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="level" label="等级" width="90">
          <template #default="{ row }">{{ levelLabel(row.level) }}</template>
        </el-table-column>
        <el-table-column prop="balance" label="余额" width="100" />
        <el-table-column prop="is_blacklisted" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_blacklisted ? 'danger' : 'success'" size="small">
              {{ row.is_blacklisted ? '已拉黑' : '正常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="date_joined" label="注册时间" width="110">
          <template #default="{ row }">{{ row.date_joined?.slice(0, 10) }}</template>
        </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
           <template #default="{ row }">
             <el-button size="small" @click="openEdit(row)">编辑</el-button>
             <el-popconfirm v-if="!row.is_blacklisted" title="确定拉黑？" @confirm="blacklistUser(row)">
               <template #reference><el-button size="small" type="warning">拉黑</el-button></template>
             </el-popconfirm>
             <el-button v-else size="small" type="success" @click="unblacklistUser(row)">取消拉黑</el-button>
             <el-popconfirm title="确定删除？" @confirm="deleteUser(row)">
               <template #reference><el-button size="small" type="danger">删除</el-button></template>
             </el-popconfirm>
           </template>
         </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :total="total"
        layout="total, prev, pager, next"
        style="margin-top:16px; justify-content:flex-end"
        @current-change="fetchData"
      />
    </el-card>

    <el-dialog v-model="dialog.visible" :title="dialog.isCreate ? '新增用户' : '编辑用户'" width="450px">
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

const roleTag = (r) => ({ admin: "danger", reception: "warning", member: "success" }[r])
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
.user-management { /* container */ }
.search-card { margin-bottom: 12px; }
</style>
