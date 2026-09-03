<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

// 响应式:用 matchMedia 检测移动端断点(<= 768px)
const MOBILE_BREAKPOINT = 768
const isMobile = ref(false)
let mediaQuery = null
let onChange = null

function checkMobile() {
  isMobile.value = window.innerWidth <= MOBILE_BREAKPOINT
}

const drawerVisible = ref(false)

// 子路由中需要展示在侧边栏的菜单项
const menus = computed(() =>
  router.options.routes
    .find((r) => r.path === '/')
    ?.children?.filter((c) => c.meta?.title)
    .map((c) => ({
      index: `/${c.path}`,
      title: c.meta?.title,
      icon: c.meta?.icon
    })) || []
)

const activeMenu = computed(() => route.path)

function handleSelect(index) {
  router.push(index)
  // 移动端:菜单点击后关闭抽屉
  if (isMobile.value) {
    drawerVisible.value = false
  }
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}

// 路由变化时,移动端自动关闭抽屉
watch(
  () => route.fullPath,
  () => {
    if (isMobile.value) drawerVisible.value = false
  }
)

onMounted(() => {
  checkMobile()
  mediaQuery = window.matchMedia(`(max-width: ${MOBILE_BREAKPOINT}px)`)
  onChange = (e) => {
    isMobile.value = e.matches
    // 切回桌面时关闭抽屉(避免遮罩残留)
    if (!e.matches) drawerVisible.value = false
  }
  // 兼容新旧 API
  if (mediaQuery.addEventListener) {
    mediaQuery.addEventListener('change', onChange)
  } else {
    mediaQuery.addListener(onChange)
  }
})

onBeforeUnmount(() => {
  if (mediaQuery) {
    if (mediaQuery.removeEventListener) {
      mediaQuery.removeEventListener('change', onChange)
    } else {
      mediaQuery.removeListener(onChange)
    }
  }
})
</script>

<template>
  <el-container class="layout">
    <!-- ========== 桌面端侧边栏(固定) ========== -->
    <el-aside v-if="!isMobile" width="220px" class="aside">
      <div class="logo">图书馆管理</div>
      <el-menu
        :default-active="activeMenu"
        background-color="#001529"
        text-color="#cfd3dc"
        active-text-color="#409eff"
        @select="handleSelect"
      >
        <el-menu-item
          v-for="item in menus"
          :key="item.index"
          :index="item.index"
        >
          <el-icon v-if="item.icon">
            <component :is="item.icon" />
          </el-icon>
          <span>{{ item.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <!-- ========== 顶部 ========== -->
      <el-header class="header">
        <div class="header-left">
          <!-- 汉堡按钮(仅移动端显示) -->
          <el-button
            v-if="isMobile"
            link
            class="hamburger"
            @click="drawerVisible = true"
          >
            <el-icon :size="22"><Menu /></el-icon>
          </el-button>
          <span class="page-title">{{ route.meta?.title }}</span>
        </div>

        <el-dropdown @command="handleLogout">
          <span class="user">
            <el-icon><UserFilled /></el-icon>
            <span class="user-name">{{ auth.user?.username || '管理员' }}</span>
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>

      <!-- ========== 内容区 ========== -->
      <el-main class="main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>

    <!-- ========== 移动端抽屉侧边栏 ========== -->
    <el-drawer
      v-if="isMobile"
      v-model="drawerVisible"
      direction="ltr"
      :size="260"
      :show-close="false"
      :with-header="false"
      class="mobile-drawer"
    >
      <div class="logo">图书馆管理</div>
      <el-menu
        :default-active="activeMenu"
        background-color="#001529"
        text-color="#cfd3dc"
        active-text-color="#409eff"
        @select="handleSelect"
      >
        <el-menu-item
          v-for="item in menus"
          :key="item.index"
          :index="item.index"
        >
          <el-icon v-if="item.icon">
            <component :is="item.icon" />
          </el-icon>
          <span>{{ item.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-drawer>
  </el-container>
</template>

<style scoped>
.layout {
  height: 100vh;
  /* 移动端防止横向溢出 */
  overflow-x: hidden;
}

/* ---------- 侧边栏(桌面) ---------- */
.aside {
  background-color: #001529;
  overflow-x: hidden;
  flex-shrink: 0;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 2px;
  background-color: #00112a;
}

.aside :deep(.el-menu) {
  border-right: none;
}

/* ---------- 顶部 ---------- */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #fff;
  border-bottom: 1px solid #ebeef5;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.hamburger {
  color: #303133;
  padding: 4px 8px;
}

.page-title {
  font-size: 16px;
  font-weight: 500;
}

.user {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  color: #303133;
}

.main {
  padding: 20px;
  background-color: #f5f7fa;
  /* 内容区允许表格内部横向滚动 */
  overflow: hidden;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* ---------- 移动端抽屉样式(深度覆盖) ---------- */
.mobile-drawer :deep(.el-drawer__body) {
  padding: 0;
  background-color: #001529;
}

.mobile-drawer :deep(.el-menu) {
  border-right: none;
}

/* ---------- 媒体查询补充:窄屏微调 ---------- */
@media (max-width: 480px) {
  .header {
    padding: 0 12px;
  }
  .page-title {
    font-size: 15px;
  }
  .user-name {
    display: none;
  }
  .main {
    padding: 12px;
  }
}
</style>
