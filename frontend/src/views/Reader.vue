<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getReadersApi,
  createReaderApi,
  updateReaderApi,
  deleteReaderApi
} from '@/api/reader'

// 读者管理:列表 + 搜索 + 增删改
const loading = ref(false)
const list = ref([])
const total = ref(0)

const query = reactive({
  keyword: '',
  page: 1,
  page_size: 10
})

const dialog = reactive({
  visible: false,
  isEdit: false,
  form: {
    id: null,
    name: '',
    gender: 'M',
    phone: '',
    email: '',
    address: '',
    card_number: ''
  }
})

const formRef = ref()
const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  card_number: [{ required: true, message: '请输入借书证号', trigger: 'blur' }]
}

async function fetchList() {
  loading.value = true
  try {
    const { items, total: t } = await getReadersApi(query)
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

function resetForm() {
  Object.assign(dialog.form, {
    id: null,
    name: '',
    gender: 'M',
    phone: '',
    email: '',
    address: '',
    card_number: ''
  })
}

function openCreate() {
  resetForm()
  dialog.isEdit = false
  dialog.visible = true
}

function openEdit(row) {
  Object.assign(dialog.form, row)
  dialog.isEdit = true
  dialog.visible = true
}

async function submit() {
  await formRef.value.validate()
  if (dialog.isEdit) {
    await updateReaderApi(dialog.form.id, dialog.form)
    ElMessage.success('更新成功')
  } else {
    await createReaderApi(dialog.form)
    ElMessage.success('新增成功')
  }
  dialog.visible = false
  fetchList()
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确认删除读者 ${row.name}?`, '提示', {
    type: 'warning'
  })
  await deleteReaderApi(row.id)
  ElMessage.success('删除成功')
  fetchList()
}

onMounted(fetchList)
</script>

<template>
  <div>
    <el-card shadow="never" class="toolbar">
      <el-form inline>
        <el-form-item label="关键词">
          <el-input
            v-model="query.keyword"
            placeholder="姓名 / 借书证号 / 手机"
            clearable
            style="width: 240px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="'Search'" @click="handleSearch">
            查询
          </el-button>
          <el-button type="success" :icon="'Plus'" @click="openCreate">
            新增读者
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never">
      <el-table v-loading="loading" :data="list" border stripe>
        <el-table-column type="index" label="#" width="50" />
        <el-table-column prop="card_number" label="借书证号" width="150" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column label="性别" width="80">
          <template #default="{ row }">
            {{ row.gender === 'F' ? '女' : '男' }}
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="手机" width="130" />
        <el-table-column prop="email" label="邮箱" min-width="160" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
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

    <el-dialog
      v-model="dialog.visible"
      :title="dialog.isEdit ? '编辑读者' : '新增读者'"
      width="520px"
    >
      <el-form ref="formRef" :model="dialog.form" :rules="rules" label-width="90px">
        <el-form-item label="借书证号" prop="card_number">
          <el-input v-model="dialog.form.card_number" />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="dialog.form.name" />
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="dialog.form.gender">
            <el-radio value="M">男</el-radio>
            <el-radio value="F">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="手机">
          <el-input v-model="dialog.form.phone" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="dialog.form.email" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="dialog.form.address" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="primary" @click="submit">确定</el-button>
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
