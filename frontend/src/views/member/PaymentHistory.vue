<template>
  <div class="payment-history">
    <header class="page-header fx-rise">
      <h2>支付记录</h2>
      <p>充值、消费与退款流水，余额实时结算</p>
    </header>

    <section class="surface ledger fx-rise">
      <header class="ledger-head">
        <div class="ledger-balance">
          <span class="field-label">账户余额</span>
          <strong class="mono">¥{{ money(balance) }}</strong>
        </div>
        <el-button type="primary" class="ledger-cta fx-press" @click="showRecharge = true">
          <el-icon class="el-icon--left"><Wallet /></el-icon>充值
        </el-button>
      </header>

      <div class="ledger-filter">
        <el-radio-group v-model="activeType" @change="fetchData">
          <el-radio-button value="">全部</el-radio-button>
          <el-radio-button value="booking">消费</el-radio-button>
          <el-radio-button value="recharge">充值</el-radio-button>
          <el-radio-button value="refund">退款</el-radio-button>
        </el-radio-group>
        <span class="ledger-count mono">{{ total }} 条</span>
      </div>

      <div class="ledger-body">
        <el-skeleton v-if="loading && !list.length" :rows="5" animated class="ledger-skeleton" />

        <template v-else>
          <el-table
            :data="list"
            v-loading="loading"
            element-loading-background="transparent"
            class="ledger-table"
          >
            <el-table-column label="类型" width="88">
              <template #default="{ row }">
                <el-tag :type="typeTag(row.type)" effect="light" round size="small">
                  {{ typeLabel(row.type) }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="金额" width="150" align="right">
              <template #default="{ row }">
                <span class="amount mono fx-tabular">¥{{ money(row.amount) }}</span>
                <span v-if="Number(row.bonus) > 0" class="amount-bonus mono fx-tabular">
                  送 ¥{{ money(row.bonus) }}
                </span>
              </template>
            </el-table-column>

            <el-table-column label="方式" width="96">
              <template #default="{ row }">
                <span class="method">{{ methodLabel(row.method) }}</span>
              </template>
            </el-table-column>

            <el-table-column label="状态" width="96">
              <template #default="{ row }">
                <el-tag :type="statusTag(row.status)" effect="light" round size="small">
                  {{ statusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="时间" min-width="170">
              <template #default="{ row }">
                <time class="time mono">{{ formatTime(row.created_at) }}</time>
              </template>
            </el-table-column>

            <template #empty>
              <div class="empty-state">
                <strong>没有匹配的支付记录</strong>
                <span>换个类型再看看，或者先充值一笔，流水会出现在这里。</span>
              </div>
            </template>
          </el-table>

          <el-pagination
            v-model:current-page="query.page"
            :total="total"
            :page-size="query.page_size"
            layout="prev, pager, next"
            @current-change="fetchData"
            class="table-footer"
          />
        </template>
      </div>
    </section>

    <el-dialog v-model="showRecharge" title="余额充值" width="440px" class="narrow-dialog">
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

      <div class="receipt">
        <span class="receipt__label">实付</span>
        <strong class="receipt__pay mono">¥{{ money(rechargeForm.amount) }}</strong>
        <span class="receipt__arrow" aria-hidden="true">→</span>
        <span class="receipt__label">到账</span>
        <strong class="receipt__get mono">¥{{ money(rechargeCredit) }}</strong>
      </div>

      <template #footer>
        <el-button @click="showRecharge = false">取消</el-button>
        <el-button type="primary" :loading="recharging" @click="handleRecharge">确认充值</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue"
import { ElMessage } from "element-plus"
import { Wallet } from "@element-plus/icons-vue"
import { paymentApi } from "@/api/payments"
import { getRechargeBonus, loadBonusTiers } from "@/utils/recharge"
import {
  money,
  paymentTypeLabel as typeLabel,
  paymentTypeTag as typeTag,
  paymentMethodLabel as methodLabel,
  paymentStatusLabel as statusLabel,
  paymentStatusTag as statusTag,
} from "@/utils/format"
import { useUserStore } from "@/store"

const userStore = useUserStore()
const list = ref([])
const total = ref(0)
const loading = ref(false)
const showRecharge = ref(false)
const recharging = ref(false)
const activeType = ref("")
const balance = ref(userStore.userInfo?.balance || 0)
const rechargeForm = reactive({ amount: 100, method: "wechat" })
const rechargeBonus = computed(() => getRechargeBonus(rechargeForm.amount))
const rechargeCredit = computed(() => Number(rechargeForm.amount || 0) + rechargeBonus.value)

const query = reactive({ page: 1, page_size: 20 })

const formatTime = (t) => (t || "").slice(0, 19).replace("T", " ")

async function fetchData() {
  loading.value = true
  try {
    const params = { ...query }
    if (activeType.value) params.type = activeType.value
    const res = await paymentApi.list(params)
    list.value = res.results || []
    total.value = res.count || 0
  } catch {
    ElMessage.error("获取支付记录失败")
  } finally {
    loading.value = false
  }
}

async function handleRecharge() {
  recharging.value = true
  try {
    const res = await paymentApi.recharge({
      amount: rechargeForm.amount,
      method: rechargeForm.method,
    })
    balance.value = res.data.balance
    userStore.userInfo.balance = res.data.balance
    const bonus = Number(res.data.bonus || 0)
    ElMessage.success(
      bonus > 0
        ? `充值成功，赠送 ¥${bonus}，余额 ¥${res.data.balance}`
        : `充值成功，余额 ¥${res.data.balance}`
    )
    showRecharge.value = false
    fetchData()
  } catch {
    ElMessage.error("充值失败")
  } finally {
    recharging.value = false
  }
}

onMounted(() => {
  fetchData()
  loadBonusTiers()
})
</script>

<style scoped>
.payment-history {
  width: 100%;
  max-width: 1040px;
  margin: 0 auto;
  padding: 28px 24px 72px;
}

.ledger {
  display: flex;
  flex-direction: column;
}

/* ---------- 余额 ---------- */

.ledger-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 20px;
  border-bottom: 1px solid var(--border-soft);
}

.ledger-balance {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.field-label {
  font-size: var(--fs-12);
  font-weight: 600;
  color: var(--ink-3);
}

.ledger-balance strong {
  font-size: var(--fs-28);
  font-weight: 800;
  line-height: 1.1;
  color: var(--ink-1);
}

.ledger-cta {
  flex: 0 0 auto;
  min-height: 40px;
  padding: 0 22px;
}

/* ---------- 筛选 ---------- */

.ledger-filter {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  flex-wrap: wrap;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border-soft);
}

.ledger-count {
  font-size: var(--fs-12);
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--ink-4);
  white-space: nowrap;
}

/* ---------- 表格 ---------- */

.ledger-body {
  padding: 4px 8px 12px;
}

.ledger-skeleton {
  padding: 18px 12px;
}

.ledger-table :deep(.el-table__cell) {
  padding: 13px 0;
}

.amount {
  font-size: var(--fs-14);
  font-weight: 700;
  color: var(--ink-1);
  white-space: nowrap;
}

.amount-bonus {
  display: block;
  font-size: var(--fs-11);
  font-weight: 700;
  color: var(--up);
}

.method,
.time {
  font-size: var(--fs-13);
  color: var(--ink-3);
}

.time {
  white-space: nowrap;
}

/* ---------- 充值弹窗 ---------- */

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

/* ---------- 动效升级（2026-10） ---------- */

/* 首屏节奏：页头先落，账本随后 */
.page-header.fx-rise {
  --i: 0;
}

.ledger.fx-rise {
  --i: 1;
}

/* 表头：一层玻璃底，滚动时吸在会员顶栏下面 */
.ledger-table {
  --el-table-row-hover-bg-color: transparent;
}

.ledger-table :deep(.el-table__header-wrapper) {
  background: var(--fx-glass-bg);
  -webkit-backdrop-filter: blur(14px) saturate(1.35);
  backdrop-filter: blur(14px) saturate(1.35);
  border-bottom: 1px solid var(--border-soft);
}

/* 只有宽屏顶栏是固定 68px；≤1080 时 MemberLayout 的导航会换行成第二排，
   --nav-h 不再等于真实顶栏高度，这时不吸顶，免得表头钻进导航底下。
   EP 的 .el-table 默认 overflow:hidden 会把 sticky 关进不滚动的 scrollport，
   这里只放开根节点，表体依旧由 .el-table__body-wrapper 自己裁。 */
@media (min-width: 1081px) {
  .ledger-table {
    overflow: visible;
  }

  .ledger-table :deep(.el-table__header-wrapper) {
    position: sticky;
    top: var(--nav-h);
    z-index: 4;
  }
}

.ledger-table :deep(.el-table__header-wrapper th.el-table__cell) {
  background-color: transparent;
}

.ledger-table :deep(.el-table__header-wrapper .cell) {
  font-size: var(--fs-12);
  font-weight: 700;
  letter-spacing: 0.04em;
  color: var(--ink-3);
}

/* 行高亮带：从左侧展开，代替 EP 默认的整格灰底 */
.ledger-table :deep(.el-table__body tr.el-table__row) {
  background-image: linear-gradient(90deg, var(--accent-soft) 0%, transparent 76%);
  background-repeat: no-repeat;
  background-position: left center;
  background-size: 0 100%;
  transition: background-size var(--dur-4) var(--ease-expo);
}

.ledger-table :deep(.el-table__body tr.el-table__row:hover) {
  background-size: 100% 100%;
}

/* 充值按钮：按下内缩（补回 EP 的颜色/投影过渡） */
.ledger-cta.fx-press {
  transition: transform var(--dur-2) var(--ease-out), background-color var(--dur-2) var(--ease-out),
    border-color var(--dur-2) var(--ease-out), box-shadow var(--dur-2) var(--ease-out),
    color var(--dur-2) var(--ease-out);
}

/* ---------- 断点 ---------- */

@media (max-width: 640px) {
  .payment-history {
    padding: 20px 16px 56px;
  }

  .ledger-head,
  .ledger-filter {
    padding: 14px 16px;
  }

  .ledger-balance strong {
    font-size: var(--fs-22);
  }

  .ledger-cta {
    min-height: 44px;
  }

  .ledger-filter :deep(.el-radio-group) {
    display: flex;
    width: 100%;
  }

  .ledger-filter :deep(.el-radio-button) {
    flex: 1;
  }

  .ledger-filter :deep(.el-radio-button__inner) {
    width: 100%;
    height: 44px;
    padding: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: var(--fs-12);
  }

  .table-footer {
    justify-content: center;
  }

  .table-footer :deep(.el-pagination) {
    flex-wrap: wrap;
    row-gap: 8px;
    justify-content: center;
  }
}
</style>

<style>
/* 弹窗挂在 body 上，作用域样式够不到；窄屏下不许横向溢出 */
.el-dialog.narrow-dialog {
  max-width: calc(100vw - 32px);
}
</style>
