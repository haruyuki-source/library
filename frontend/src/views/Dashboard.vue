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
  { label: '图书总数', value: 0, icon: 'Reading', to: '/book' },
  { label: '读者总数', value: 0, icon: 'User', to: '/reader' },
  { label: '借阅中', value: 0, icon: 'Switch', to: '/borrow' },
  { label: '分类数', value: 0, icon: 'Files', to: '/category' }
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
            <el-icon class="stat-icon">
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
  border: none;
  border-radius: 14px;
  /* 统一渐变,与全站卡片一致 */
  background: var(--card-gradient);
  transition: transform 0.2s, box-shadow 0.2s;
  /* 移动端:移除 300ms 点击延迟,确保触控立即响应 */
  touch-action: manipulation;
  -webkit-tap-highlight-color: rgba(236, 107, 154, 0.18);
  box-shadow: var(--card-shadow);
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--card-shadow-hover);
}
.stat-card:active {
  transform: scale(0.98);
}

.stat-body {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.stat-icon {
  /* 统一:四个图标同色深粉 */
  width: 48px;
  height: 48px;
  border-radius: 10px;
  background: #f48fb1;
  color: #fff;
  font-size: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-text {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.stat-value {
  font-size: 22px;
  font-weight: 600;
  color: #880e4f;
  line-height: 1.2;
  white-space: nowrap;
}

.stat-label {
  color: #ad1457;
  font-size: 13px;
  margin-top: 4px;
  /* 关键:防止中文标签被挤成竖排 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stat-arrow {
  color: #f48fb1;
  font-size: 16px;
  flex-shrink: 0;
}

/* 移动端:进一步压缩卡片内边距与图标,给文字留足横向空间 */
@media (max-width: 480px) {
  .stat-card :deep(.el-card__body) {
    padding: 14px 12px !important;
  }
  .stat-body {
    gap: 10px;
  }
  .stat-icon {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
  .stat-value {
    font-size: 20px;
  }
  .stat-label {
    font-size: 12px;
  }
}

.welcome {
  margin-top: 20px;
  border: none;
  border-radius: 14px;
  /* 统一渐变,与全站卡片一致 */
  background: var(--card-gradient);
  box-shadow: var(--card-shadow);
}

.welcome h3 {
  margin: 0 0 8px;
  color: #880e4f;
}

.welcome p {
  margin: 0;
  color: #ad1457;
}
</style>
