<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getBooksApi } from '@/api/book'
import { getReadersApi } from '@/api/reader'
import { getCategoriesApi } from '@/api/category'
import { getBorrowsApi } from '@/api/borrow'

const router = useRouter()

// 仪表盘:统计卡片(对接后端真实数据,点击可跳转对应页面)
const stats = ref([
  { label: '图书总数', value: 0, icon: 'Reading', color: '#409eff', to: '/book' },
  { label: '读者总数', value: 0, icon: 'User', color: '#67c23a', to: '/reader' },
  { label: '借阅中', value: 0, icon: 'Switch', color: '#e6a23c', to: '/borrow' },
  { label: '分类数', value: 0, icon: 'Files', color: '#f56c6c', to: '/category' }
])

function goTo(path) {
  router.push(path)
}

const loading = ref(false)

async function fetchStats() {
  loading.value = true
  try {
    // 并行请求 4 个统计数据
    const [books, readers, categories, borrows] = await Promise.all([
      getBooksApi({ page_size: 1 }),
      getReadersApi({ page_size: 1 }),
      getCategoriesApi(),
      getBorrowsApi({ status: 'borrowed', page_size: 1 })
    ])
    stats.value[0].value = books.total || 0
    stats.value[1].value = readers.total || 0
    stats.value[2].value = borrows.total || 0
    stats.value[3].value = categories.total || 0
  } catch (err) {
    // 接口错误已由 request 拦截器统一提示
  } finally {
    loading.value = false
  }
}

onMounted(fetchStats)
</script>

<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col
        v-for="item in stats"
        :key="item.label"
        :xs="12"
        :sm="12"
        :md="6"
      >
        <el-card
          class="stat-card"
          shadow="hover"
          :body-style="{ padding: '18px' }"
          @click="goTo(item.to)"
        >
          <div class="stat-body" @click.stop="goTo(item.to)">
            <el-icon class="stat-icon" :style="{ background: item.color }">
              <component :is="item.icon" />
            </el-icon>
            <div class="stat-text">
              <div class="stat-value">{{ item.value }}</div>
              <div class="stat-label">{{ item.label }}</div>
            </div>
            <el-icon class="stat-arrow"><ArrowRight /></el-icon>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="welcome" shadow="never">
      <h3>欢迎使用图书馆管理系统</h3>
      <p>左侧菜单可进行图书、读者、分类与借阅管理。</p>
    </el-card>
  </div>
</template>

<style scoped>
.stat-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  /* 移动端:移除 300ms 点击延迟,确保触控立即响应 */
  touch-action: manipulation;
  -webkit-tap-highlight-color: rgba(64, 158, 255, 0.1);
}
.stat-card:hover {
  transform: translateY(-2px);
}
.stat-card:active {
  transform: scale(0.98);
}

.stat-body {
  display: flex;
  align-items: center;
  gap: 14px;
  cursor: pointer;
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 8px;
  color: #fff;
  font-size: 26px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-text {
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  color: #909399;
  font-size: 13px;
  margin-top: 4px;
}

.stat-arrow {
  color: #c0c4cc;
  font-size: 16px;
  flex-shrink: 0;
}

.welcome {
  margin-top: 20px;
}

.welcome h3 {
  margin: 0 0 8px;
}

.welcome p {
  margin: 0;
  color: #909399;
}
</style>
