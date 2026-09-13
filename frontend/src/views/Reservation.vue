<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getReservationsApi,
  fulfillReservationApi,
  cancelReservationAdminApi
} from '@/api/reservation'

// 预约管理:学生线上预约,到馆柜台扫码/录入预约号后确认借书(转借阅+扣库存)
const loading = ref(false)
const list = ref([])
const total = ref(0)
const actionId = ref(null)

// 默认只看待办理预约,方便柜台作业
const query = reactive({
  status: 'reserved',
  page: 1,
  page_size: 10
})

// 扫码枪等价于键盘输入 + 回车:录入预约号快速办理
const quickId = ref('')

const statusOptions = [
  { value: 'reserved', label: '预约中' },
  { value: 'fulfilled', label: '已办理' },
  { value: 'cancelled', label: '已取消' }
]

function statusText(status) {
  return { reserved: '预约中', fulfilled: '已办理', cancelled: '已取消' }[status] || status
}
function statusType(status) {
  return { reserved: 'primary', fulfilled: 'success', cancelled: 'info' }[status] || 'info'
}

async function fetchList() {
  loading.value = true
  try {
    const params = { ...query }
    if (!params.status) delete params.status
    const { items, total: t } = await getReservationsApi(params)
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

async function handleFulfill(row) {
  try {
    await ElMessageBox.confirm(
      `确认为读者 ${row.reader?.card_no || ''} ${row.reader?.name || ''} 办理《${row.book?.title || ''}》借书?办理后图书状态变为借阅中并扣减 1 本可借库存。`,
      '到馆确认借书',
      { confirmButtonText: '确认办理', cancelButtonText: '取消', type: 'info' }
    )
  } catch (action) {
    return
  }
  actionId.value = row.id
  try {
    const data = await fulfillReservationApi(row.id)
    ElMessage.success(
      `办理成功,应还日期 ${data.borrow_record?.due_date || ''},剩余库存 ${row.book?.available_quantity ?? ''}`
    )
    await fetchList()
  } catch (err) {
    // 错误已由 request 拦截器统一提示(如库存不足/重复借阅)
  } finally {
    actionId.value = null
  }
}

// 扫码/录入预约号回车:先在列表中定位,定位不到则直接按号办理
async function handleQuickFulfill() {
  const id = Number(String(quickId.value).trim())
  if (!id) return
  const row = list.value.find((r) => r.id === id && r.status === 'reserved')
  if (row) {
    quickId.value = ''
    return handleFulfill(row)
  }
  actionId.value = id
  try {
    const data = await fulfillReservationApi(id)
    ElMessage.success(`预约 #${id} 办理成功,应还日期 ${data.borrow_record?.due_date || ''}`)
    quickId.value = ''
    await fetchList()
  } catch (err) {
    // 统一提示
  } finally {
    actionId.value = null
  }
}

async function handleCancel(row) {
  try {
    await ElMessageBox.confirm(
      `确认取消预约 #${row.id}(《${row.book?.title || ''}》)?`,
      '取消预约',
      { confirmButtonText: '确认取消', cancelButton: '再想想', type: 'warning' }
    )
  } catch (action) {
    return
  }
  actionId.value = row.id
  try {
    await cancelReservationAdminApi(row.id)
    ElMessage.success('预约已取消')
    await fetchList()
  } catch (err) {
    // 统一提示
  } finally {
    actionId.value = null
  }
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
            style="width: 140px"
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
        <el-form-item label="扫码/预约号">
          <el-input
            v-model="quickId"
            placeholder="扫码或录入预约号后回车办理"
            style="width: 230px"
            clearable
            @keyup.enter="handleQuickFulfill"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="success" :icon="'Check'" @click="handleQuickFulfill">
            快速办理
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never">
      <el-table v-loading="loading" :data="list" border stripe>
        <el-table-column prop="id" label="预约号" width="80" />
        <el-table-column label="书名" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">{{ row.book?.title || '-' }}</template>
        </el-table-column>
        <el-table-column label="读者" width="150" class-name="hide-mobile">
          <template #default="{ row }">
            {{ row.reader?.card_no || '-' }} {{ row.reader?.name || '' }}
          </template>
        </el-table-column>
        <el-table-column prop="reserve_date" label="预约日期" width="110" class-name="hide-mobile" />
        <el-table-column prop="expire_date" label="保留至" width="110" class-name="hide-mobile" />
        <el-table-column label="当前库存" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="(row.book?.available_quantity || 0) > 0 ? 'success' : 'danger'" size="small">
              {{ row.book?.available_quantity ?? '-' }}/{{ row.book?.total_quantity ?? '-' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">
              {{ statusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center">
          <template #default="{ row }">
            <template v-if="row.status === 'reserved'">
              <el-button
                type="primary"
                link
                size="small"
                :loading="actionId === row.id"
                @click="handleFulfill(row)"
              >
                确认借书
              </el-button>
              <el-button
                type="danger"
                link
                size="small"
                :disabled="actionId === row.id"
                @click="handleCancel(row)"
              >
                取消
              </el-button>
            </template>
            <span v-else-if="row.status === 'fulfilled'" class="due-text">
              应还 {{ row.due_date || '-' }}
            </span>
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
