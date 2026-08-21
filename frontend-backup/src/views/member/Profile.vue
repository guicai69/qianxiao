<template>
  <div class="profile-page">
    <el-card class="profile-card">
      <template #header><h3>个人中心</h3></template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="手机号">{{ userInfo.phone }}</el-descriptions-item>
        <el-descriptions-item label="昵称">{{ userInfo.nickname || '未设置' }}</el-descriptions-item>
        <el-descriptions-item label="角色">
          <el-tag :type="roleTag(userInfo.role)" size="small">{{ roleLabel(userInfo.role) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="会员等级">{{ levelLabel(userInfo.level) }}</el-descriptions-item>
        <el-descriptions-item label="余额">¥{{ userInfo.balance }}</el-descriptions-item>
        <el-descriptions-item label="注册时间">{{ userInfo.date_joined?.slice(0, 10) }}</el-descriptions-item>
      </el-descriptions>

      <div style="margin-top:20px; display:flex; gap:12px;">
        <el-button type="primary" @click="editDialog = true">修改昵称</el-button>
        <el-button type="warning" @click="pwdDialog = true">修改密码</el-button>
      </div>
    </el-card>

    <!-- 修改昵称 -->
    <el-dialog v-model="editDialog" title="修改昵称" width="400px">
      <el-form :model="editForm">
        <el-form-item label="昵称">
          <el-input v-model="editForm.nickname" placeholder="请输入昵称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveNickname">保存</el-button>
      </template>
    </el-dialog>

    <!-- 修改密码 -->
    <el-dialog v-model="pwdDialog" title="修改密码" width="420px">
      <el-form ref="pwdRef" :model="pwdForm" :rules="pwdRules" label-width="90px">
        <el-form-item label="旧密码" prop="old_password">
          <el-input v-model="pwdForm.old_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="pwdForm.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认新密码" prop="new_password2">
          <el-input v-model="pwdForm.new_password2" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwdDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="savePassword">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'
import { useUserStore } from '@/store'

const userStore = useUserStore()
const userInfo = userStore.userInfo || {}

const editDialog = ref(false)
const pwdDialog = ref(false)
const saving = ref(false)
const pwdRef = ref(null)

const editForm = reactive({ nickname: userInfo.nickname || '' })

const pwdForm = reactive({ old_password: '', new_password: '', new_password2: '' })
const validatePwd2 = (_r, v, cb) => v !== pwdForm.new_password ? cb(new Error('两次密码不一致')) : cb()
const pwdRules = {
  old_password: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' },
  ],
  new_password2: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validatePwd2, trigger: 'blur' },
  ],
}

const roleTag = (r) => ({ admin: 'danger', reception: 'warning', member: 'success' }[r])
const roleLabel = (r) => ({ admin: '管理员', reception: '前台', member: '会员' }[r])
const levelLabel = (l) => ({ normal: '普通会员', gold: '金卡会员' }[l])

async function saveNickname() {
  saving.value = true
  try {
    const res = await api.patch('users/me/', { nickname: editForm.nickname })
    userStore.setUserInfo(res.data)
    ElMessage.success('昵称已更新')
    editDialog.value = false
  } catch { /* handled */ } finally { saving.value = false }
}

async function savePassword() {
  if (!pwdRef.value) return
  await pwdRef.value.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      await api.post('auth/change-password/', { ...pwdForm })
      ElMessage.success('密码修改成功，请重新登录')
      userStore.clearToken()
      window.location.href = '/login'
    } catch { /* handled */ } finally { saving.value = false }
  })
}
</script>

<style scoped>
.profile-page { max-width: 800px; margin: 0 auto; }
.profile-card h3 { margin: 0; }
</style>
