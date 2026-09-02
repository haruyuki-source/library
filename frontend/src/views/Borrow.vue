<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getBorrowsApi,
  borrowBookApi,
  returnBookApi,
  renewBookApi,
  deleteBorrowApi
} from '@/api/borrow'

// 借阅管理:列表 + 借书 + 还书 + 续借
const loading = ref(false)
const list = ref([])
const total = ref(0)

const query = reactive({
  status: '',
  page: 1,
  page_size: 10
})

const dialog = reactive({
  visible: false,
  form: { book_id: null, reader_id: null, due_days: 30, remark: '' }
})

const renewDialog = reactive({
  visible: false,
  id: null,
  extra_days: 30
})

const formRef = ref()
const rules = {
  book_id: [{ required: true, message: '请输入图书ID', trigger: 'blur' }],
  reader_id: [{ required: true, message: '请输入读者ID', trigger: 'blur' }]
}

async function fetchList() {
  loading.value = true
  try {
    const { items, total: t } = await getBorrowsApi(query)
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

async function submitBorrow() {
  await formRef.value.validate()
  await borrowBookApi(dialog.form)
  ElMessage.success('借阅成功')
  dialog.visible = false
  Object.assign(dialog.form, { book_id: null, reader_id: null, due_days: 30, remark: '' })
  fetchList()
}

async function handleReturn(row) {
  await ElMessageBox.confirm('确认归还该书?', '提示', { type: 'warning' })
  await returnBookApi(row.id, {})
  ElMessage.success('归还成功')
  fetchList()
}

function openRenew(row) {
  renewDialog.id = row.id
  renewDialog.extra_days = 30
  renewDialog.visible = true
}

async function submitRenew() {
  await renewBookApi(renewDialog.id, { extra_days: renewDialog.extra_days })
  ElMessage.success('续借成功')
  renewDialog.visible = false
  fetchList()
}

async function handleDelete(row) {
  await ElMessageBox.confirm('确认删除该借阅记录?', '提示', {
    type: 'warning'
  })
  await deleteBorrowApi(row.id)
  ElMessage.success('删除成功')
  fetchList()
}

function statusText(status) {
  return {
    borrowed: '借阅中',
    returned: '已归还',
    overdue: '已逾期',
    lost: '遗失'
  }[status] || status
}

function statusType(status) {
  return {
    borrowed: 'warning',
    returned: 'success',
    overdue: 'danger',
    lost: 'info'
  }[status] || 'info'
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
          >
            <el-option label="借阅中" value="borrowed" />
            <el-option label="已归还" value="returned" />
            <el-option label="已逾期" value="overdue" />
            <el-option label="遗失" value="lost" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="'Search'" @click="handleSearch">
            查询
          </el-button>
          <el-button type="success" :icon="'Plus'" @click="dialog.visible = true">
            新增借阅
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never">
      <el-table v-loading="loading" :data="list" border stripe>
        <el-table-column type="index" label="#" width="50" />
        <el-table-column label="书名" min-width="160">
          <template #default="{ row }">{{ row.book?.title || '-' }}</template>
        </el-table-column>
        <el-table-column label="读者" width="120">
          <template #default="{ row }">{{ row.reader?.name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="borrow_date" label="借阅日期" width="120" />
        <el-table-column prop="due_date" label="应还日期" width="120" />
        <el-table-column prop="return_date" label="归还日期" width="120" />
        <el-table-column prop="renew_count" label="续借" width="70" align="center" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">
              {{ statusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="230" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'borrowed' || row.status === 'overdue'"
              link
              type="primary"
              @click="handleReturn(row)"
            >
              归还
            </el-button>
            <el-button
              v-if="row.status === 'borrowed'"
              link
              type="warning"
              @click="openRenew(row)"
            >
              续借
            </el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
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

    <el-dialog v-model="dialog.visible" title="新增借阅" width="460px">
      <el-form ref="formRef" :model="dialog.form" :rules="rules" label-width="90px">
        <el-form-item label="图书ID" prop="book_id">
          <el-input-number v-model="dialog.form.book_id" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="读者ID" prop="reader_id">
          <el-input-number v-model="dialog.form.reader_id" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="借阅天数">
          <el-input-number v-model="dialog.form.due_days" :min="1" :max="180" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="dialog.form.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="primary" @click="submitBorrow">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="renewDialog.visible" title="续借" width="380px">
      <el-form label-width="90px">
        <el-form-item label="续借天数">
          <el-input-number v-model="renewDialog.extra_days" :min="1" :max="180" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="renewDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="submitRenew">确定</el-button>
      </template>
    </el-dialog>
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
