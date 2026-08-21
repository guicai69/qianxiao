<template>
  <div class="profile-page">
    <div class="page-header">
      <h2>个人中心</h2>
      <p>账号资料、密码与余额管理</p>
    </div>

    <div class="profile-grid">
      <el-card shadow="never" class="profile-summary">
        <div class="profile-hero">
          <span class="avatar">{{ initial }}</span>
          <div class="profile-copy">
            <strong>{{ userInfo.nickname || userInfo.phone }}</strong>
            <span>{{ roleLabel(userInfo.role) }}</span>
          </div>
        </div>

        <div class="balance-panel">
          <span>当前余额</span>
          <strong>¥{{ userInfo.balance }}</strong>
          <el-button type="primary" round @click="rechargeDialog = true">
            <el-icon class="el-icon--left"><Wallet /></el-icon>余额充值
          </el-button>
        </div>

        <div v-if="userInfo.role === 'member'" class="growth-panel">
          <div class="growth-head">
            <span>会员成长</span>
            <strong>{{ levelLabel(userInfo.level) }}</strong>
          </div>
          <el-progress
            :percentage="levelProgress.percent"
            :stroke-width="10"
            :show-text="false"
            color="#1976d2"
          />
          <span class="growth-hint">{{ levelProgress.text }}</span>
        </div>
      </el-card>

      <el-card shadow="never" class="profile-detail">
        <template #header>
          <span class="detail-title">账号资料</span>
        </template>

        <el-descriptions :column="1" border>
          <el-descriptions-item label="手机号">{{ userInfo.phone }}</el-descriptions-item>
          <el-descriptions-item label="昵称">{{ userInfo.nickname || "未设置" }}</el-descriptions-item>
          <el-descriptions-item label="角色">
            <el-tag :type="roleTag(userInfo.role)" effect="light" round size="small">
              {{ roleLabel(userInfo.role) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="会员等级">{{ levelLabel(userInfo.level) }}</el-descriptions-item>
          <el-descriptions-item v-if="userInfo.role === 'member'" label="会员折扣">{{ discountText(userInfo.level) }}</el-descriptions-item>
          <el-descriptions-item label="余额">¥{{ userInfo.balance }}</el-descriptions-item>
          <el-descriptions-item label="注册时间">{{ userInfo.date_joined?.slice(0, 10) }}</el-descriptions-item>
        </el-descriptions>

        <div class="profile-actions">
          <el-button @click="editDialog = true">
            <el-icon class="el-icon--left"><User /></el-icon>修改昵称
          </el-button>
          <el-button @click="pwdDialog = true">
            <el-icon class="el-icon--left"><Lock /></el-icon>修改密码
          </el-button>
          <el-button type="primary" @click="rechargeDialog = true">
            <el-icon class="el-icon--left"><Wallet /></el-icon>余额充值
          </el-button>
        </div>
      </el-card>
    </div>

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

    <el-dialog v-model="rechargeDialog" title="余额充值" width="380px">
      <el-form :model="rechargeForm" label-width="80px">
        <el-form-item label="充值金额">
          <el-input-number v-model="rechargeForm.amount" :min="1" :step="50" style="width: 210px" />
        </el-form-item>
        <el-form-item label="支付方式">
          <el-radio-group v-model="rechargeForm.method">
            <el-radio value="wechat">微信支付</el-radio>
            <el-radio value="alipay">支付宝</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <div class="recharge-bonus">
        <span>充值赠送</span>
        <strong>¥{{ rechargeBonus }}，到账 ¥{{ rechargeBonus + rechargeForm.amount }}</strong>
      </div>
      <template #footer>
        <el-button @click="rechargeDialog = false">取消</el-button>
        <el-button type="primary" :loading="recharging" @click="handleRecharge">确认充值</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from "vue"
import { ElMessage } from "element-plus"
import { User, Lock, Wallet } from "@element-plus/icons-vue"
import api from "@/api"
import { paymentApi } from "@/api/payments"
import { getRechargeBonus } from "@/utils/recharge"
import { useUserStore } from "@/store"

const userStore = useUserStore()
const userInfo = userStore.userInfo || {}

const editDialog = ref(false)
const pwdDialog = ref(false)
const rechargeDialog = ref(false)
const recharging = ref(false)
const saving = ref(false)
const pwdRef = ref(null)

const editForm = reactive({ nickname: userInfo.nickname || "" })
const rechargeForm = reactive({ amount: 100, method: "wechat" })

const pwdForm = reactive({ old_password: "", new_password: "", new_password2: "" })
const validatePwd2 = (_r, v, cb) =>
  v !== pwdForm.new_password ? cb(new Error("两次密码不一致")) : cb()
const pwdRules = {
  old_password: [{ required: true, message: "请输入旧密码", trigger: "blur" }],
  new_password: [
    { required: true, message: "请输入新密码", trigger: "blur" },
    { min: 6, message: "密码至少6位", trigger: "blur" },
  ],
  new_password2: [
    { required: true, message: "请确认新密码", trigger: "blur" },
    { validator: validatePwd2, trigger: "blur" },
  ],
}

const initial = computed(() => (userInfo.nickname || userInfo.phone || "U").slice(0, 1))
const roleTag = (r) => ({ admin: "danger", reception: "warning", member: "success" }[r])
const roleLabel = (r) => ({ admin: "管理员", reception: "前台", member: "会员" }[r])
const levelLabel = (l) => ({ normal: "普通会员", silver: "银卡会员", gold: "金卡会员" }[l] || l)
const discountText = (l) =>
  ({ normal: "原价", silver: "95折", gold: "90折" }[l] || "原价")

const rechargeBonus = computed(() => getRechargeBonus(rechargeForm.amount))

const levelProgress = computed(() => {
  const total = Number(userInfo.total_spend || 0)
  if (userInfo.level === "gold") {
    return { percent: 100, text: "已达最高等级 · 金卡会员" }
  }
  if (userInfo.level === "silver") {
    const percent = Math.min(100, Math.round((total / 2000) * 100))
    return { percent, text: `再消费 ¥${Math.max(0, 2000 - total)} 升级金卡会员` }
  }
  const percent = Math.min(100, Math.round((total / 500) * 100))
  return { percent, text: `再消费 ¥${Math.max(0, 500 - total)} 升级银卡会员` }
})

async function saveNickname() {
  saving.value = true
  try {
    const res = await api.patch("users/me/", { nickname: editForm.nickname })
    userStore.setUserInfo(res.data)
    ElMessage.success("昵称已更新")
    editDialog.value = false
  } catch {
    // handled by interceptor
  } finally {
    saving.value = false
  }
}

async function savePassword() {
  if (!pwdRef.value) return
  await pwdRef.value.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      await api.post("auth/change-password/", { ...pwdForm })
      ElMessage.success("密码修改成功，请重新登录")
      userStore.clearToken()
      window.location.href = "/login"
    } catch {
      // handled by interceptor
    } finally {
      saving.value = false
    }
  })
}

async function handleRecharge() {
  recharging.value = true
  try {
    const res = await paymentApi.recharge(rechargeForm)
    userStore.userInfo.balance = res.data.balance
    userStore.setUserInfo(userStore.userInfo)
    const bonus = Number(res.data.bonus || 0)
    ElMessage.success(
      bonus > 0
        ? `充值成功，赠送 ¥${bonus}，余额 ¥${res.data.balance}`
        : `充值成功，余额 ¥${res.data.balance}`
    )
    rechargeDialog.value = false
  } catch {
    ElMessage.error("充值失败")
  } finally {
    recharging.value = false
  }
}
</script>

<style scoped>
.profile-page {
  width: 100%;
  max-width: 960px;
  margin: 0 auto;
}

.profile-grid {
  display: grid;
  grid-template-columns: 340px minmax(0, 1fr);
  gap: 16px;
}

.profile-summary {
  height: fit-content;
}

.profile-summary :deep(.el-card__body) {
  padding: 24px;
}

.profile-hero {
  display: flex;
  align-items: center;
  gap: 14px;
}

.avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 16px;
  color: #ffffff;
  background: var(--mui-primary);
  font-size: 22px;
  font-weight: 800;
}

.profile-copy {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.profile-copy strong {
  color: var(--mui-text);
  font-size: 17px;
  font-weight: 800;
}

.profile-copy span {
  margin-top: 4px;
  color: var(--mui-muted);
  font-size: 13px;
}

.balance-panel {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 8px;
  margin-top: 24px;
  padding: 18px;
  border: 1px solid #dbeafe;
  border-radius: 14px;
  background: #f8fbff;
}

.balance-panel span {
  color: var(--mui-muted);
  font-size: 13px;
  font-weight: 600;
}

.balance-panel strong {
  color: var(--mui-primary);
  font-size: 30px;
  font-weight: 800;
}

.balance-panel .el-button {
  margin-top: 8px;
}

.growth-panel {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 16px;
  padding: 16px 18px;
  border: 1px solid var(--mui-border);
  border-radius: 14px;
  background: #ffffff;
}

.growth-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.growth-head span {
  color: var(--mui-muted);
  font-size: 13px;
  font-weight: 600;
}

.growth-head strong {
  color: var(--mui-primary);
  font-size: 13px;
  font-weight: 800;
}

.growth-hint {
  color: var(--mui-muted);
  font-size: 12px;
}

.recharge-bonus {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 6px;
  padding: 10px 14px;
  border-radius: 10px;
  color: var(--mui-muted);
  background: #f8fafc;
  font-size: 13px;
}

.recharge-bonus strong {
  color: var(--mui-primary);
  font-weight: 800;
}

.detail-title {
  font-weight: 700;
}

.profile-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 20px;
}

@media (max-width: 800px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
}
</style>
