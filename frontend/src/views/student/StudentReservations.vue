<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getStudentReservationsApi,
  cancelReservationApi
} from '@/api/student'

// 我的预约:查看预约记录,预约中可取消
const loading = ref(false)
const list = ref([])
const total = ref(0)
const cancellingId = ref(null)

const query = reactive({
  status: '',
  page: 1,
  page_size: 10
})

const statusOptions = [
  { value: 'reserved', label: '预约中' },
  { value: 'fulfilled', label: '已办理(借阅中)' },
  { value: 'cancelled', label: '已取消' }
]

function statusTag(status) {
  return { reserved: 'primary', fulfilled: 'success', cancelled: 'info' }[status] || 'info'
}

function statusText(status) {
  return { reserved: '预约中', fulfilled: '已办理', cancelled: '已取消' }[status] || status
}

async function fetchList() {
  loading.value = true
  try {
    const params = { ...query }
    if (!params.status) delete params.status
    const { items, total: t } = await getStudentReservationsApi(params)
    list.value = items || []
    total.value = t || 0
  } catch (err) {
    list.value = []
  } finally {
    loading.value = false
  }
}

async function handleCancel(row) {
  try {
    await ElMessageBox.confirm(
      `确认取消《${row.book?.title || '该书'}》的预约吗?取消后名额将立即释放。`,
      '取消预约',
      { confirmButtonText: '确认取消', cancelButtonText: '再想想', type: 'warning' }
    )
  } catch (action) {
    return
  }
  cancellingId.value = row.id
  try {
    await cancelReservationApi(row.id)
    ElMessage.success('预约已取消')
    await fetchList()
  } catch (err) {
    // 错误已由 request 拦截器统一提示
  } finally {
    cancellingId.value = null
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
            style="width: 170px"
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
        <el-table-column label="书名" min-width="170" show-overflow-tooltip>
          <template #default="{ row }">{{ row.book?.title || '-' }}</template>
        </el-table-column>
        <el-table-column label="作者" width="120" show-overflow-tooltip class-name="hide-mobile">
          <template #default="{ row }">{{ row.book?.author || '-' }}</template>
        </el-table-column>
        <el-table-column prop="reserve_date" label="预约日期" width="110" />
        <el-table-column prop="expire_date" label="保留至" width="110" />
        <el-table-column label="办理/应还" width="120" class-name="hide-mobile">
          <template #default="{ row }">
            <span v-if="row.status === 'fulfilled'">
              {{ row.fulfill_date }}<br />
              <span class="due-text">应还 {{ row.due_date || '-' }}</span>
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'reserved'"
              type="danger"
              link
              size="small"
              :loading="cancellingId === row.id"
              @click="handleCancel(row)"
            >
              取消预约
            </el-button>
            <span v-else class="muted">-</span>
          </template>
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
.due-text {
  font-size: 12px;
  color: #c2185b;
}
.muted {
  color: #c0c4cc;
}
</style>
