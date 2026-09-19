<template>
  <div class="profile-page">
    <header class="page-header">
      <h2>个人中心</h2>
      <p>账号资料、会员等级与余额充值</p>
    </header>

    <div class="profile-grid">
      <!-- 左栏：身份 → 余额 → 等级，一条竖着读的信息流 -->
      <section class="surface profile-card">
        <div class="identity">
          <span class="avatar">{{ initial }}</span>
          <div class="identity-copy">
            <strong>{{ userInfo.nickname || userInfo.phone }}</strong>
            <span>{{ roleLabel(userInfo.role) }}</span>
          </div>
        </div>

        <div class="balance">
          <span class="field-label">账户余额</span>
          <strong class="balance-value mono">¥{{ money(userInfo.balance) }}</strong>
          <p class="balance-note">余额可直接支付场地费用，充值满档另有赠送</p>
          <el-button type="primary" class="balance-cta" @click="rechargeDialog = true">
            <el-icon class="el-icon--left"><Wallet /></el-icon>余额充值
          </el-button>
        </div>

        <div v-if="userInfo.role === 'member'" class="tiers">
          <div class="tiers-head">
            <span class="field-label">会员等级</span>
            <strong>{{ levelLabel(userInfo.level) }}</strong>
          </div>

          <ol class="rail">
            <li
              v-for="t in tiers"
              :key="t.key"
              :class="{ 'is-passed': t.passed, 'is-current': t.current }"
            >
              <span class="rail-dot" aria-hidden="true"></span>
              <span class="rail-name">{{ t.name }}</span>
              <span class="rail-rate mono">{{ t.rate }}</span>
            </li>
          </ol>

          <p class="tiers-hint">
            <template v-if="nextTier">
              累计消费 <b class="mono">¥{{ money(spend) }}</b><br />
              再消费 <b class="mono">¥{{ money(nextTier.need) }}</b> 升级{{ nextTier.name }}
            </template>
            <template v-else>
              累计消费 <b class="mono">¥{{ money(spend) }}</b><br />
              已是最高等级，场地费用按 {{ discountText(userInfo.level) }} 结算
            </template>
          </p>
        </div>
      </section>

      <!-- 右栏：资料，用发丝线分行，不做成一格一格的卡片 -->
      <section class="surface profile-detail">
        <header class="panel-head">
          <h3>账号资料</h3>
          <span class="panel-note">手机号即登录账号</span>
        </header>

        <dl class="facts">
          <div class="fact">
            <dt>手机号</dt>
            <dd class="mono">{{ userInfo.phone }}</dd>
          </div>
          <div class="fact">
            <dt>昵称</dt>
            <dd>{{ userInfo.nickname || '未设置' }}</dd>
          </div>
          <div class="fact">
            <dt>角色</dt>
            <dd>
              <el-tag :type="roleTag(userInfo.role)" effect="light" round size="small">
                {{ roleLabel(userInfo.role) }}
              </el-tag>
            </dd>
          </div>
          <div class="fact">
            <dt>会员等级</dt>
            <dd>{{ levelLabel(userInfo.level) }}</dd>
          </div>
          <div v-if="userInfo.role === 'member'" class="fact">
            <dt>会员折扣</dt>
            <dd>{{ discountText(userInfo.level) }}</dd>
          </div>
          <div class="fact">
            <dt>账户余额</dt>
            <dd class="mono accent">¥{{ money(userInfo.balance) }}</dd>
          </div>
          <div class="fact">
            <dt>注册时间</dt>
            <dd class="mono">{{ joinedAt }}</dd>
          </div>
        </dl>

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
      </section>
    </div>

    <el-dialog v-model="editDialog" title="修改昵称" width="400px" class="narrow-dialog">
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

    <el-dialog v-model="pwdDialog" title="修改密码" width="420px" class="narrow-dialog">
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

    <el-dialog v-model="rechargeDialog" title="余额充值" width="440px" class="narrow-dialog">
      <div class="tier-picker">
        <button
          v-for="t in rechargeTiers"
          :key="t.amount"
          type="button"
          class="tier-card"
          :class="{ 'is-active': Number(rechargeForm.amount) === t.amount }"
          :aria-pressed="Number(rechargeForm.amount) === t.amount"
          @click="rechargeForm.amount = t.amount"
        >
          <span class="tier-card__amount mono">¥{{ t.amount }}</span>
          <span class="tier-card__bonus">{{ t.bonus ? `送 ¥${t.bonus}` : '无赠送' }}</span>
        </button>
      </div>

      <el-form :model="rechargeForm" label-width="80px" class="recharge-form">
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

      <div class="receipt">
        <span class="receipt__label">实付</span>
        <strong class="receipt__pay mono">¥{{ money(rechargeForm.amount) }}</strong>
        <span class="receipt__arrow" aria-hidden="true">→</span>
        <span class="receipt__label">到账</span>
        <strong class="receipt__get mono">¥{{ money(rechargeCredit) }}</strong>
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
import { getRechargeBonus, RECHARGE_BONUS_TIERS } from "@/utils/recharge"
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

const money = (v) => Number(v || 0).toFixed(2)
const joinedAt = computed(() => userInfo.date_joined?.slice(0, 10) || "未记录")

const rechargeTiers = RECHARGE_BONUS_TIERS
const rechargeBonus = computed(() => getRechargeBonus(rechargeForm.amount))
const rechargeCredit = computed(() => Number(rechargeForm.amount || 0) + rechargeBonus.value)

// 等级阶梯：阈值与折扣跟后端一致，只做展示。
// 用「已走过 / 当前」的节点表达进度，不编百分比。
const LEVEL_TIERS = [
  { key: "normal", name: "普通会员", rate: "原价", at: 0 },
  { key: "silver", name: "银卡会员", rate: "95折", at: 500 },
  { key: "gold", name: "金卡会员", rate: "90折", at: 2000 },
]

const spend = computed(() => Number(userInfo.total_spend || 0))

const currentTierIndex = computed(() => {
  const i = LEVEL_TIERS.findIndex((t) => t.key === userInfo.level)
  return i < 0 ? 0 : i
})

const tiers = computed(() =>
  LEVEL_TIERS.map((t, i) => ({
    ...t,
    passed: i <= currentTierIndex.value,
    current: i === currentTierIndex.value,
  }))
)

const nextTier = computed(() => {
  const next = LEVEL_TIERS[currentTierIndex.value + 1]
  if (!next) return null
  return { ...next, need: Math.max(0, next.at - spend.value) }
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
  max-width: 1040px;
  margin: 0 auto;
  padding: 28px 24px 72px;
}

.profile-grid {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  gap: 16px;
  align-items: start;
}

.profile-card {
  display: flex;
  flex-direction: column;
  padding: 20px;
}

/* ---------- 身份 ---------- */

.identity {
  display: flex;
  align-items: center;
  gap: 14px;
  padding-bottom: 18px;
  border-bottom: 1px solid var(--border-soft);
}

.avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  flex: 0 0 48px;
  border-radius: var(--radius);
  color: var(--on-accent);
  background: var(--accent);
  font-size: var(--fs-18);
  font-weight: 800;
}

.identity-copy {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.identity-copy strong {
  font-size: var(--fs-16);
  font-weight: 800;
  color: var(--ink-1);
  overflow-wrap: anywhere;
}

.identity-copy span {
  font-size: var(--fs-12);
  color: var(--ink-3);
}

/* ---------- 余额 ---------- */

.field-label {
  font-size: var(--fs-12);
  font-weight: 600;
  color: var(--ink-3);
}

.balance {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 18px 0;
  border-bottom: 1px solid var(--border-soft);
}

.balance-value {
  font-size: var(--fs-36);
  font-weight: 800;
  line-height: 1.1;
  color: var(--ink-1);
}

.balance-note {
  margin: 0;
  font-size: var(--fs-12);
  line-height: var(--lh-body);
  color: var(--ink-3);
}

.balance-cta {
  width: 100%;
  height: 40px;
  margin-top: 8px;
}

/* ---------- 等级：一条走过的阶梯 ---------- */

.tiers {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-top: 18px;
}

.tiers-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
}

.tiers-head strong {
  font-size: var(--fs-13);
  font-weight: 800;
  color: var(--accent);
}

.rail {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin: 0;
  padding: 0;
  list-style: none;
}

.rail li {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding-top: 22px;
  min-width: 0;
}

.rail li::before {
  content: "";
  position: absolute;
  top: 5px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--border);
}

.rail li:first-child::before {
  left: 6px;
  border-radius: 2px 0 0 2px;
}

.rail li:last-child::before {
  right: 6px;
  border-radius: 0 2px 2px 0;
}

.rail-dot {
  position: absolute;
  top: 0;
  left: 0;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--surface);
  border: 2px solid var(--border-strong);
}

.rail li.is-passed::before {
  background: var(--accent);
}

.rail li.is-passed .rail-dot {
  background: var(--accent);
  border-color: var(--accent);
}

.rail li.is-current .rail-dot {
  box-shadow: 0 0 0 4px var(--accent-soft);
}

.rail-name {
  font-size: var(--fs-12);
  font-weight: 700;
  color: var(--ink-3);
}

.rail li.is-passed .rail-name {
  color: var(--ink-1);
}

.rail-rate {
  font-size: var(--fs-11);
  color: var(--ink-4);
}

.tiers-hint {
  margin: 0;
  font-size: var(--fs-12);
  line-height: var(--lh-body);
  color: var(--ink-3);
}

.tiers-hint b {
  font-weight: 700;
  color: var(--ink-1);
}

/* ---------- 资料 ---------- */

.profile-detail {
  display: flex;
  flex-direction: column;
}

.panel-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-soft);
}

.panel-head h3 {
  margin: 0;
  font-size: var(--fs-14);
  font-weight: 700;
  color: var(--ink-1);
}

.panel-note {
  font-size: var(--fs-12);
  color: var(--ink-4);
}

.facts {
  margin: 0;
  padding: 4px 20px;
}

.fact {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  min-height: 46px;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-soft);
}

.fact:last-child {
  border-bottom: 0;
}

.fact dt {
  flex: 0 0 auto;
  font-size: var(--fs-13);
  color: var(--ink-3);
}

.fact dd {
  margin: 0;
  font-size: var(--fs-13);
  font-weight: 600;
  color: var(--ink-1);
  text-align: right;
  overflow-wrap: anywhere;
}

.fact dd.accent {
  color: var(--accent);
  font-weight: 700;
}

.profile-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: auto;
  padding: 16px 20px 20px;
  border-top: 1px solid var(--border-soft);
}

.profile-actions :deep(.el-button) {
  min-height: 40px;
}

/* ---------- 充值弹窗 ---------- */

.tier-picker {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.tier-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  min-height: 64px;
  padding: 12px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
  cursor: pointer;
  text-align: left;
  transition: border-color var(--dur-2) var(--ease-out),
    background-color var(--dur-2) var(--ease-out), box-shadow var(--dur-2) var(--ease-out);
}

.tier-card:hover {
  border-color: var(--border-strong);
}

.tier-card.is-active {
  border-color: var(--accent);
  background: var(--accent-soft);
  box-shadow: inset 0 0 0 1px var(--accent);
}

.tier-card__amount {
  font-size: var(--fs-18);
  font-weight: 800;
  color: var(--ink-1);
}

.tier-card.is-active .tier-card__amount {
  color: var(--accent);
}

.tier-card__bonus {
  font-size: var(--fs-12);
  color: var(--ink-3);
}

.recharge-form {
  margin-top: 18px;
}

.receipt {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 8px 10px;
  padding: 12px 14px;
  border: 1px dashed var(--border-strong);
  border-radius: var(--radius);
  font-size: var(--fs-13);
}

.receipt__label {
  color: var(--ink-3);
}

.receipt__pay {
  font-size: var(--fs-16);
  font-weight: 800;
  color: var(--ink-1);
}

.receipt__arrow {
  color: var(--ink-4);
}

.receipt__get {
  font-size: var(--fs-16);
  font-weight: 800;
  color: var(--accent);
}

.receipt__note {
  font-size: var(--fs-11);
  color: var(--ink-4);
}

/* ---------- 断点 ---------- */

@media (max-width: 860px) {
  .profile-grid {
    grid-template-columns: minmax(0, 1fr);
  }
}

@media (max-width: 640px) {
  .profile-page {
    padding: 20px 16px 56px;
  }

  .balance-value {
    font-size: var(--fs-28);
  }

  .profile-actions :deep(.el-button) {
    flex: 1 1 100%;
    min-height: 44px;
  }
}
</style>

<style>
/* 弹窗挂在 body 上，作用域样式够不到；窄屏下不许横向溢出 */
.el-dialog.narrow-dialog {
  max-width: calc(100vw - 32px);
}
</style>
