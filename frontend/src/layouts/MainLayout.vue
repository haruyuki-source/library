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
  // 移动端:先关闭抽屉,再跳转
  if (isMobile.value) {
    drawerVisible.value = false
    // 等待抽屉关闭动画后再跳转,避免视觉卡顿
    setTimeout(() => router.push(index), 200)
  } else {
    router.push(index)
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
        background-color="transparent"
        text-color="#880e4f"
        active-text-color="#c2185b"
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
        background-color="transparent"
        text-color="#880e4f"
        active-text-color="#c2185b"
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
  background: linear-gradient(180deg, #fce4ec 0%, #f8bbd0 100%);
  overflow-x: hidden;
  flex-shrink: 0;
}

.logo {
  height: 50px;
  line-height: 50px;
  text-align: center;
  color: #880e4f;
  font-size: 17px;
  font-weight: 600;
  letter-spacing: 2px;
  background-color: rgba(248, 187, 208, 0.3);
  border-bottom: 1px solid rgba(194, 24, 91, 0.12);
}

.aside :deep(.el-menu) {
  border-right: none;
}

/* 菜单项:左侧 active 指示条 + 悬停底色 */
.aside :deep(.el-menu-item),
.mobile-drawer :deep(.el-menu-item) {
  height: 48px;
  line-height: 48px;
  margin: 4px 8px;
  border-radius: 6px;
  position: relative;
  transition: background-color 0.2s;
}

.aside :deep(.el-menu-item:hover),
.mobile-drawer :deep(.el-menu-item:hover) {
  background-color: rgba(244, 143, 177, 0.25) !important;
}

/* active 菜单项:左侧深粉指示条 + 高亮 */
.aside :deep(.el-menu-item.is-active),
.mobile-drawer :deep(.el-menu-item.is-active) {
  background-color: rgba(194, 24, 91, 0.15) !important;
  color: #c2185b !important;
}

.aside :deep(.el-menu-item.is-active)::before,
.mobile-drawer :deep(.el-menu-item.is-active)::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background-color: #c2185b;
  border-radius: 0 2px 2px 0;
}

/* ---------- 顶部 ---------- */
.header {
  /* 与侧边栏 logo 同高,保证左右对齐 */
  height: 50px;
  line-height: 50px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  /* 与侧边栏同色,去掉白色 */
  background: linear-gradient(90deg, #fce4ec 0%, #fde8ef 100%);
  border-bottom: 1px solid rgba(194, 24, 91, 0.12);
  box-shadow: 0 1px 4px rgba(236, 107, 154, 0.1);
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.hamburger {
  color: #880e4f;
  padding: 4px 8px;
}

.page-title {
  font-size: 16px;
  font-weight: 500;
  color: #880e4f;
}

.user {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  color: #ad1457;
}

.main {
  padding: 20px;
  /* 纯淡粉渐变背景,与 body 保持一致 */
  background: linear-gradient(135deg, #fef4f7 0%, #fce4ec 50%, #f8bbd0 100%);
  /* 内容区允许纵向滚动 + 表格内部横向滚动 */
  overflow: auto;
}

/* ---------- 内容区滚动条(可见 + 悬停加粗) ---------- */
.main {
  scrollbar-width: thin;
  scrollbar-color: #c0c4cc transparent;
}

.main::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

.main::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 6px;
}

.main::-webkit-scrollbar-thumb {
  background-color: #c0c4cc;
  border-radius: 6px;
  border: 2px solid transparent;
  background-clip: content-box;
  transition: background-color 0.2s;
}

.main::-webkit-scrollbar-thumb:hover {
  background-color: #909399;
  background-clip: content-box;
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
.mobile-drawer :deep(.el-drawer) {
  background: linear-gradient(180deg, #fce4ec 0%, #f8bbd0 100%);
}

.mobile-drawer :deep(.el-drawer__body) {
  padding: 0;
  background: linear-gradient(180deg, #fce4ec 0%, #f8bbd0 100%);
  height: 100%;
  overflow-y: auto;
}

.mobile-drawer :deep(.el-menu) {
  border-right: none;
  background: transparent;
  /* 让菜单至少撑满抽屉,避免底部出现白色空隙 */
  min-height: 100%;
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
