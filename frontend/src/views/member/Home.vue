<template>
  <div class="member-home">
    <section class="home-hero">
      <div class="hero-copy">
        <div class="eyebrow">
          <span class="eyebrow-dot"></span>
          羽毛球馆预约
        </div>
        <h1>选择场馆，快速预约</h1>
        <p>登录后即可查看场馆、场地与可预约时段。</p>
        <el-button type="primary" size="large" class="hero-button" @click="handleStartBooking">
          开始预约
          <el-icon class="el-icon--right"><ArrowRight /></el-icon>
        </el-button>
      </div>

      <div class="hero-visual" aria-hidden="true">
        <div class="court-panel">
          <div class="court-title">
            <el-icon><Medal /></el-icon>
            <span>COURT 01</span>
          </div>
          <div class="court-lines">
            <span class="line line-a"></span>
            <span class="line line-b"></span>
            <span class="line line-c"></span>
          </div>
          <div class="court-meta">
            <span>19:00 - 22:00</span>
            <span>¥60</span>
          </div>
        </div>
      </div>
    </section>

    <section v-if="announcements.length" class="announce-section">
      <div class="section-heading">
        <h3>场馆公告</h3>
        <span>Announcements</span>
      </div>
      <div class="announce-list">
        <el-card
          v-for="a in announcements"
          :key="a.id"
          shadow="never"
          class="announce-card"
        >
          <div class="announce-card-head">
            <strong>{{ a.title }}</strong>
            <el-tag v-if="a.is_pinned" type="danger" effect="light" round size="small">置顶</el-tag>
          </div>
          <p>{{ a.content }}</p>
          <span class="announce-date">{{ formatTime(a.created_at) }}</span>
        </el-card>
      </div>
    </section>

    <section class="quick-grid">
      <el-card
        v-for="item in quickActions"
        :key="item.label"
        shadow="never"
        class="quick-card"
        @click="go(item.path)"
      >
        <div class="quick-card-inner">
          <span class="quick-icon" :style="{ color: item.color, background: item.soft }">
            <el-icon :size="24"><component :is="item.icon" /></el-icon>
          </span>
          <div>
            <strong>{{ item.label }}</strong>
            <span>{{ item.description }}</span>
          </div>
        </div>
      </el-card>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import { useUserStore } from "@/store"
import { OfficeBuilding, Tickets, User, ArrowRight, Medal } from "@element-plus/icons-vue"
import { announcementApi } from "@/api/announcements"

const router = useRouter()
const userStore = useUserStore()
const announcements = ref([])

function formatTime(t) {
  return (t || "").slice(0, 16).replace("T", " ")
}

onMounted(async () => {
  try {
    const res = await announcementApi.list({ page_size: 5 })
    announcements.value = res.results || []
  } catch {
    // 未登录或网络异常时忽略
  }
})

const quickActions = [
  {
    label: "选择场馆",
    description: "查看可预约场地",
    path: "/venues",
    icon: OfficeBuilding,
    color: "#1976d2",
    soft: "#e8f1fb",
  },
  {
    label: "我的订单",
    description: "查看预约与支付",
    path: "/orders",
    icon: Tickets,
    color: "#d97706",
    soft: "#fffbeb",
  },
  {
    label: "个人中心",
    description: "资料与余额充值",
    path: "/profile",
    icon: User,
    color: "#16a34a",
    soft: "#ecfdf5",
  },
]

function go(path) {
  if (!userStore.isLoggedIn) router.push("/login")
  else router.push(path)
}

function handleStartBooking() {
  if (!userStore.isLoggedIn) router.push("/login")
  else if (userStore.isAdmin) router.push("/admin/dashboard")
  else if (userStore.isReception) router.push("/reception/dashboard")
  else router.push("/venues")
}
</script>

<style scoped>
.member-home {
  width: 100%;
  max-width: 1180px;
  margin: 0 auto;
}

.home-hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(360px, 480px);
  align-items: center;
  gap: 40px;
  min-height: 360px;
  padding: 44px 48px;
  border: 1px solid var(--mui-border);
  border-radius: 20px;
  background: var(--mui-surface);
  box-shadow: var(--mui-shadow);
}

.hero-copy {
  max-width: 520px;
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 18px;
  color: var(--mui-primary);
  font-size: 13px;
  font-weight: 700;
}

.eyebrow-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--mui-primary);
}

.hero-copy h1 {
  margin: 0 0 14px;
  color: var(--mui-text);
  font-size: 40px;
  font-weight: 800;
  line-height: 1.2;
  letter-spacing: 0;
}

.hero-copy p {
  margin: 0 0 28px;
  color: var(--mui-muted);
  font-size: 15px;
  line-height: 1.7;
}

.hero-button {
  height: 48px;
  padding: 0 24px;
  font-size: 15px;
}

.hero-visual {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 280px;
  padding: 20px;
  border-radius: 18px;
  background: #f8fafc;
}

.court-panel {
  width: 100%;
  max-width: 360px;
  padding: 22px;
  border: 1px solid #dbeafe;
  border-radius: 16px;
  background: var(--mui-surface);
  box-shadow: var(--mui-shadow);
}

.court-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--mui-primary);
  font-size: 15px;
  font-weight: 800;
}

.court-lines {
  position: relative;
  height: 170px;
  margin: 18px 0;
  border: 2px solid #cbd5e1;
  border-radius: 4px;
}

.line {
  position: absolute;
  background: #cbd5e1;
}

.line-a {
  top: 50%;
  left: 0;
  right: 0;
  height: 2px;
}

.line-b {
  top: 0;
  left: 50%;
  bottom: 0;
  width: 2px;
}

.line-c {
  top: 0;
  left: 50%;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: transparent;
  border: 2px solid #cbd5e1;
  transform: translate(-50%, -50%);
}

.court-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: var(--mui-muted);
  font-size: 13px;
  font-weight: 700;
}

.announce-section {
  margin-top: 24px;
}

.section-heading {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 14px;
}

.section-heading h3 {
  margin: 0;
  color: var(--mui-text);
  font-size: 20px;
  font-weight: 800;
}

.section-heading span {
  color: var(--mui-muted);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.announce-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 14px;
}

.announce-card {
  border-left: 3px solid var(--mui-primary);
}

.announce-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 8px;
}

.announce-card-head strong {
  color: var(--mui-text);
  font-size: 15px;
  font-weight: 800;
}

.announce-card p {
  margin: 0 0 10px;
  color: #475569;
  font-size: 13px;
  line-height: 1.7;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.announce-date {
  color: var(--mui-muted);
  font-size: 12px;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.quick-card {
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}

.quick-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--mui-shadow-lg);
  border-color: #bfdbfe;
}

.quick-card-inner {
  display: flex;
  align-items: center;
  gap: 14px;
}

.quick-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 14px;
  flex: 0 0 48px;
}

.quick-card-inner div {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.quick-card-inner strong {
  color: var(--mui-text);
  font-size: 15px;
  font-weight: 800;
}

.quick-card-inner span {
  margin-top: 4px;
  color: var(--mui-muted);
  font-size: 13px;
}

@media (max-width: 900px) {
  .home-hero {
    grid-template-columns: 1fr;
    padding: 32px 24px;
  }

  .hero-copy h1 {
    font-size: 32px;
  }

  .quick-grid {
    grid-template-columns: 1fr;
  }
}
</style>
