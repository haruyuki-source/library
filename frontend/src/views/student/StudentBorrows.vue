<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getStudentBorrowsApi } from '@/api/student'

// 学生端我的借阅:仅本人记录,状态筛选 + 分页
const loading = ref(false)
const list = ref([])
const total = ref(0)

const query = reactive({
  status: '',
  page: 1,
  page_size: 10
})

const statusOptions = [
  { value: 'borrowed', label: '借阅中' },
  { value: 'returned', label: '已归还' },
  { value: 'overdue', label: '逾期' },
  { value: 'lost', label: '遗失' }
]

function statusTag(status) {
  return { borrowed: 'warning', returned: 'success', overdue: 'danger', lost: 'info' }[status] || 'info'
}

function statusText(status) {
  return { borrowed: '借阅中', returned: '已归还', overdue: '逾期', lost: '遗失' }[status] || status
}

async function fetchList() {
  loading.value = true
  try {
    const params = { ...query }
    if (!params.status) delete params.status
    const { items, total: t } = await getStudentBorrowsApi(params)
    list.value = items || []
    total.value = t || 0
  } catch (err) {
    list.value = []
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  query.page = 1
  fetchList()
}

onMounted(fetchList)
</script>

<template>
  <div>
    <el-card shadow="never" class="toolbar">
      <el-form inline>
        <el-form-item label="状态">
          <el-select
            v-model="query.status"
            placeholder="全部"
            clearable
            style="width: 160px"
            @change="handleSearch"
          >
            <el-option
              v-for="opt in statusOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="'Search'" @click="handleSearch">
            查询
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never">
      <el-table v-loading="loading" :data="list" border stripe>
        <el-table-column type="index" label="#" width="50" />
        <el-table-column label="书名" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">{{ row.book?.title || '-' }}</template>
        </el-table-column>
        <el-table-column label="作者" width="130" show-overflow-tooltip class-name="hide-mobile">
          <template #default="{ row }">{{ row.book?.author || '-' }}</template>
        </el-table-column>
        <el-table-column prop="borrow_date" label="借阅日期" width="110" />
        <el-table-column prop="due_date" label="应还日期" width="110" />
        <el-table-column prop="return_date" label="归还日期" width="110" class-name="hide-mobile">
          <template #default="{ row }">{{ row.return_date || '-' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="罚金" width="80" align="center" class-name="hide-mobile">
          <template #default="{ row }">¥{{ (row.fine_amount || 0).toFixed(2) }}</template>
        </el-table-column>
      </el-table>

      <el-pagination
        class="pager"
        background
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :page-sizes="[10, 20, 50]"
        @current-change="fetchList"
        @size-change="fetchList"
      />
    </el-card>
  </div>
</template>

<style scoped>
.toolbar {
  margin-bottom: 16px;
}
.pager {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>
