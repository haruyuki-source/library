import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

// 路由表:登录页 + 主布局下的 5 个业务模块
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '首页概览', icon: 'HomeFilled' }
      },
      {
        path: 'book',
        name: 'Book',
        component: () => import('@/views/Book.vue'),
        meta: { title: '图书管理', icon: 'Reading' }
      },
      {
        path: 'reader',
        name: 'Reader',
        component: () => import('@/views/Reader.vue'),
        meta: { title: '读者管理', icon: 'User' }
      },
      {
        path: 'category',
        name: 'Category',
        component: () => import('@/views/Category.vue'),
        meta: { title: '分类管理', icon: 'Files' }
      },
      {
        path: 'borrow',
        name: 'Borrow',
        component: () => import('@/views/Borrow.vue'),
        meta: { title: '借阅管理', icon: 'Switch' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '404', requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫:校验登录态
router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  document.title = to.meta.title
    ? `${to.meta.title} - 图书馆管理系统`
    : '图书馆管理系统'

  if (to.meta.requiresAuth === false) {
    // 已登录用户访问登录页则跳转首页
    if (to.name === 'Login' && auth.token) {
      return next({ path: '/' })
    }
    return next()
  }

  if (!auth.token) {
    return next({ path: '/login', query: { redirect: to.fullPath } })
  }
  next()
})

export default router
