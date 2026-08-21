import { createRouter, createWebHistory } from 'vue-router'
import NProgress from 'nprogress'
import { useUserStore } from '@/store'

NProgress.configure({ showSpinner: false })

const routes = [
  // Admin routes
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    redirect: '/admin/dashboard',
    meta: { roles: ['admin', 'reception'] },
    children: [
      { path: 'dashboard', component: () => import('@/views/admin/Dashboard.vue'), meta: { title: '数据看板' } },
      { path: 'users', component: () => import('@/views/admin/UserManagement.vue'), meta: { title: '用户管理', roles: ['admin'] } },
      { path: 'venues', component: () => import('@/views/admin/VenueManagement.vue'), meta: { title: '场馆管理' } },
      { path: 'venues/:id/courts', component: () => import('@/views/admin/CourtManagement.vue'), meta: { title: '场地管理' } },
      { path: 'venues/:id/timeslots', component: () => import('@/views/admin/TimeSlotManagement.vue'), meta: { title: '时段管理' } },
      { path: 'bookings', component: () => import('@/views/admin/BookingManagement.vue'), meta: { title: '预约管理' } },
      { path: 'payments', component: () => import('@/views/admin/PaymentHistory.vue'), meta: { title: '支付记录' } },
      { path: 'announcements', component: () => import('@/views/admin/AnnouncementManagement.vue'), meta: { title: '公告管理' } },
    ],
  },
  // Reception routes
  {
    path: '/reception',
    component: () => import('@/layouts/AdminLayout.vue'),
    redirect: '/reception/dashboard',
    meta: { roles: ['reception'] },
    children: [
      { path: 'dashboard', component: () => import('@/views/reception/Dashboard.vue'), meta: { title: '操作台' } },
    ],
  },
  // Member routes
  {
    path: '/',
    component: () => import('@/layouts/MemberLayout.vue'),
    children: [
      { path: '', component: () => import('@/views/member/Home.vue'), meta: { title: '首页' } },
      { path: 'profile', component: () => import('@/views/member/Profile.vue'), meta: { title: '个人中心', auth: true } },
      { path: 'venues', component: () => import('@/views/member/VenueList.vue'), meta: { title: '选择场馆', auth: true } },
      { path: 'venues/:id', component: () => import('@/views/member/VenueDetail.vue'), meta: { title: '场馆详情', auth: true } },
      { path: 'orders', component: () => import('@/views/member/MemberOrders.vue'), meta: { title: '我的订单', auth: true } },
      { path: 'payments', component: () => import('@/views/member/PaymentHistory.vue'), meta: { title: '支付记录', auth: true } },
    ],
  },
  // Auth
  { path: '/login', name: 'Login', component: () => import('@/views/Login.vue'), meta: { guest: true } },
  { path: '/register', name: 'Register', component: () => import('@/views/Register.vue'), meta: { guest: true } },
  // 404
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('@/views/NotFound.vue') },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, _from, next) => {
  NProgress.start()
  const userStore = useUserStore()
  const token = userStore.token
  if (to.meta.guest) {
    if (token && userStore.userInfo) {
      if (userStore.isAdmin) return next('/admin/dashboard')
      if (userStore.isReception) return next('/reception/dashboard')
      return next('/')
    }
    return next()
  }
  if (to.meta.auth && !token) return next('/login')
  if (to.meta.roles) {
    if (!token) return next('/login')
    if (!to.meta.roles.includes(userStore.role)) {
      if (userStore.isAdmin) return next('/admin/dashboard')
      if (userStore.isReception) return next('/reception/dashboard')
      return next('/')
    }
  }
  next()
})

router.afterEach(() => {
  NProgress.done()
})

router.onError(() => {
  NProgress.done()
})

export default router
