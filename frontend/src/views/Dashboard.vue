<script setup>
import { ref, onMounted } from 'vue'
import { getBooksApi } from '@/api/book'
import { getReadersApi } from '@/api/reader'
import { getCategoriesApi } from '@/api/category'
import { getBorrowsApi } from '@/api/borrow'

// 仪表盘:统计卡片(对接后端真实数据)
const stats = ref([
  { label: '图书总数', value: 0, icon: 'Reading', color: '#409eff' },
  { label: '读者总数', value: 0, icon: 'User', color: '#67c23a' },
  { label: '借阅中', value: 0, icon: 'Switch', color: '#e6a23c' },
  { label: '分类数', value: 0, icon: 'Files', color: '#f56c6c' }
])

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
        <el-card class="stat-card" shadow="hover">
          <div class="stat-body">
            <el-icon class="stat-icon" :style="{ background: item.color }">
              <component :is="item.icon" />
            </el-icon>
            <div class="stat-text">
              <div class="stat-value">{{ item.value }}</div>
              <div class="stat-label">{{ item.label }}</div>
            </div>
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
}

.stat-body {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 8px;
  color: #fff;
  font-size: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.stat-label {
  color: #909399;
  font-size: 13px;
  margin-top: 4px;
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
