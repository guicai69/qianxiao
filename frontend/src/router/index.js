import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  // Admin routes
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    redirect: '/admin/dashboard',
    children: [
      { path: 'dashboard', component: () => import('@/views/admin/Dashboard.vue') },
    ],
  },
  // Reception routes
  {
    path: '/reception',
    component: () => import('@/layouts/AdminLayout.vue'),
    redirect: '/reception/dashboard',
    children: [
      { path: 'dashboard', component: () => import('@/views/reception/Dashboard.vue') },
    ],
  },
  // Member routes
  {
    path: '/',
    component: () => import('@/layouts/MemberLayout.vue'),
    children: [
      { path: '', component: () => import('@/views/member/Home.vue') },
    ],
  },
  // Auth
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
  },
  // 404
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
