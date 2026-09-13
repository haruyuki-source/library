import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useStudentStore } from '@/store/student'

// 路由表:双端登录页 + 管理布局 + 学生布局
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/student/login',
    name: 'StudentLogin',
    component: () => import('@/views/Login.vue'),
    meta: { title: '学生登录', requiresAuth: false }
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
      },
      {
        path: 'reservation',
        name: 'Reservation',
        component: () => import('@/views/Reservation.vue'),
        meta: { title: '预约管理', icon: 'Stamp' }
      }
    ]
  },
  {
    path: '/student',
    component: () => import('@/layouts/StudentLayout.vue'),
    redirect: '/student/books',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'books',
        name: 'StudentBooks',
        component: () => import('@/views/student/StudentBooks.vue'),
        meta: { title: '图书检索', icon: 'Search' }
      },
      {
        path: 'reservations',
        name: 'StudentReservations',
        component: () => import('@/views/student/StudentReservations.vue'),
        meta: { title: '我的预约', icon: 'Calendar' }
      },
      {
        path: 'borrows',
        name: 'StudentBorrows',
        component: () => import('@/views/student/StudentBorrows.vue'),
        meta: { title: '我的借阅', icon: 'Notebook' }
      },
      {
        path: 'profile',
        name: 'StudentProfile',
        component: () => import('@/views/student/StudentProfile.vue'),
        meta: { title: '个人信息', icon: 'User' }
      },
      {
        path: 'password',
        name: 'StudentPassword',
        component: () => import('@/views/student/StudentPassword.vue'),
        meta: { title: '修改密码', icon: 'Lock' }
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

// 全局前置守卫:按路径前缀分流校验双端登录态
router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  const student = useStudentStore()
  document.title = to.meta.title
    ? `${to.meta.title} - 图书馆管理系统`
    : '图书馆管理系统'

  // 学生端:/student/* 统一校验 student_token
  if (to.path.startsWith('/student')) {
    if (to.name === 'StudentLogin') {
      // 已登录学生访问登录页则跳学生首页
      if (student.token) {
        return next({ path: '/student/books' })
      }
      return next()
    }
    if (!student.token) {
      return next({ path: '/student/login', query: { redirect: to.fullPath } })
    }
    return next()
  }

  // 管理端
  if (to.meta.requiresAuth === false) {
    // 已登录管理员访问登录页则跳首页
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
