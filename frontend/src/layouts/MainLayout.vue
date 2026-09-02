<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

// 子路由中需要展示在侧边栏的菜单项
const menus = computed(() =>
  router.options.routes
    .find((r) => r.path === '/')
    ?.children?.map((c) => ({
      index: `/${c.path}`,
      title: c.meta?.title,
      icon: c.meta?.icon
    })) || []
)

const activeMenu = computed(() => route.path)

function handleSelect(index) {
  router.push(index)
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <el-container class="layout">
    <!-- 侧边栏:菜单根据路由配置生成 -->
    <el-aside width="220px" class="aside">
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
      <!-- 顶部:用户信息 + 登出 -->
      <el-header class="header">
        <span class="page-title">{{ route.meta?.title }}</span>
        <el-dropdown @command="handleLogout">
          <span class="user">
            <el-icon><UserFilled /></el-icon>
            {{ auth.user?.username || '管理员' }}
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>

      <!-- 内容区:嵌套路由出口 -->
      <el-main class="main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout {
  height: 100vh;
}

.aside {
  background-color: #001529;
  overflow-x: hidden;
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

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #fff;
  border-bottom: 1px solid #ebeef5;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
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
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
