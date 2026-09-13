<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getBooksApi } from '@/api/book'
import { getCategoriesApi } from '@/api/category'
import {
  getStudentActiveBorrowsApi,
  getStudentReservationsApi,
  reserveBookApi
} from '@/api/student'
import { useStudentStore } from '@/store/student'

// 学生端图书检索 + 线上预约索书(预约不扣库存,到馆由管理员办理)
const student = useStudentStore()
const BORROW_DAYS = 30 // 到馆办理后的借阅期限,用于确认提示

const loading = ref(false)
const list = ref([])
const total = ref(0)
const categories = ref([])

// 在借图书:book_id -> 借阅记录
const activeMap = ref(new Map())
// 预约中图书:book_id -> 预约记录
const reservedMap = ref(new Map())
const activeCount = computed(() => activeMap.value.size)
const reservedCount = computed(() => reservedMap.value.size)
const maxBorrow = computed(() => student.user?.max_borrow || 0)
const quotaFull = computed(() => activeCount.value + reservedCount.value >= maxBorrow.value)
// 当前正在提交预约的图书 id(防止重复点击)
const reservingId = ref(null)

const query = reactive({
  keyword: '',
  category_id: null,
  page: 1,
  page_size: 10
})

async function fetchList() {
  loading.value = true
  try {
    const params = { ...query }
    if (!params.category_id) delete params.category_id
    const { items, total: t } = await getBooksApi(params)
    list.value = items || []
    total.value = t || 0
  } catch (err) {
    list.value = []
  } finally {
    loading.value = false
  }
}

async function fetchCategories() {
  try {
    const data = await getCategoriesApi()
    categories.value = data?.items || []
  } catch (err) {
    categories.value = []
  }
}

async function fetchActive() {
  try {
    const data = await getStudentActiveBorrowsApi()
    activeMap.value = new Map((data.items || []).map((r) => [r.book_id, r]))
  } catch (err) {
    activeMap.value = new Map()
  }
}

async function fetchReserved() {
  try {
    const data = await getStudentReservationsApi({ status: 'reserved', page_size: 100 })
    reservedMap.value = new Map((data.items || []).map((r) => [r.book_id, r]))
  } catch (err) {
    reservedMap.value = new Map()
  }
}

// 预约按钮状态:reserved 预约中 / active 在借 / limit 名额满 / reserveable 可预约
function reserveState(row) {
  if (reservedMap.value.has(row.id)) return 'reserved'
  if (activeMap.value.has(row.id)) return 'active'
  if (quotaFull.value) return 'limit'
  return 'reserveable'
}

function formatDate(d) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

async function handleReserve(row) {
  if (reserveState(row) !== 'reserveable' || reservingId.value) return
  // 办理借书当日起算借阅期限,展示预计应还日期
  const due = new Date()
  due.setDate(due.getDate() + BORROW_DAYS)

  try {
    await ElMessageBox.confirm(
      `确认预约《${row.title}》吗？预约成功后，请前往图书馆柜台办理借书手续，借阅期限 ${BORROW_DAYS} 天。预计应还日期：${formatDate(due)}`,
      '预约确认',
      { confirmButtonText: '确认预约', cancelButtonText: '取消', type: 'info' }
    )
  } catch (action) {
    return // 用户取消
  }

  reservingId.value = row.id
  try {
    // 以接口真实返回作为成功依据;预约不扣库存
    const rec = await reserveBookApi(row.id)
    ElMessage.success(`预约成功,请在 ${rec.expire_date} 前到馆办理借书手续`)
    await fetchReserved()
  } catch (err) {
    // 错误已由 request 拦截器统一提示
  } finally {
    reservingId.value = null
  }
}

function handleSearch() {
  query.page = 1
  fetchList()
}

onMounted(() => {
  fetchCategories()
  fetchActive()
  fetchReserved()
  fetchList()
})
</script>

<template>
  <div>
    <el-card shadow="never" class="toolbar">
      <el-form inline>
        <el-form-item label="关键词">
          <el-input
            v-model="query.keyword"
            placeholder="书名 / 作者 / ISBN"
            clearable
            style="width: 240px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="分类">
          <el-select
            v-model="query.category_id"
            placeholder="全部分类"
            clearable
            style="width: 180px"
            @change="handleSearch"
          >
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
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

    <el-alert
      :title="`当前在借 ${activeCount} 本,预约中 ${reservedCount} 本,合计名额 ${activeCount + reservedCount} / ${maxBorrow};预约不扣减库存,请在保留期(7 天)内到馆办理`"
      :type="quotaFull ? 'warning' : 'success'"
      :closable="false"
      show-icon
      class="quota-tip"
    />

    <el-card shadow="never">
      <el-table v-loading="loading" :data="list" border stripe>
        <el-table-column type="index" label="#" width="50" />
        <el-table-column prop="title" label="书名" min-width="180" show-overflow-tooltip />
        <el-table-column prop="author" label="作者" width="130" show-overflow-tooltip class-name="hide-mobile" />
        <el-table-column prop="isbn" label="ISBN" width="140" class-name="hide-mobile" />
        <el-table-column label="分类" width="120" class-name="hide-mobile">
          <template #default="{ row }">{{ row.category?.name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="location" label="馆藏位置" width="100" class-name="hide-mobile" />
        <el-table-column label="库存" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.available_quantity > 0 ? 'success' : 'info'">
              {{ row.available_quantity > 0 ? '可借' : '已借完' }}
              {{ row.available_quantity }}/{{ row.total_quantity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="110" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="reserveState(row) === 'reserveable'"
              type="primary"
              size="small"
              :loading="reservingId === row.id"
              @click="handleReserve(row)"
            >
              预约
            </el-button>
            <el-tag v-else-if="reserveState(row) === 'reserved'" type="primary" size="small">
              预约中
            </el-tag>
            <el-tag v-else-if="reserveState(row) === 'active'" type="warning" size="small">
              借阅中
            </el-tag>
            <el-tooltip
              v-else-if="reserveState(row) === 'limit'"
              :content="`在借与预约合计已达上限(${maxBorrow} 本)`"
              placement="top"
            >
              <el-button type="primary" size="small" disabled>预约</el-button>
            </el-tooltip>
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
.quota-tip {
  margin-bottom: 16px;
}
.pager {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>
