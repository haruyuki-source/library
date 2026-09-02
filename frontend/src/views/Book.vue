<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getBooksApi,
  createBookApi,
  updateBookApi,
  deleteBookApi
} from '@/api/book'
import { getCategoriesApi } from '@/api/category'

// 图书管理:列表 + 搜索 + 增删改
const loading = ref(false)
const list = ref([])
const total = ref(0)
const categories = ref([])

const query = reactive({
  keyword: '',
  page: 1,
  page_size: 10
})

function emptyForm() {
  return {
    id: null,
    title: '',
    author: '',
    isbn: '',
    publisher: '',
    publish_year: null,
    category_id: null,
    location: '',
    total_quantity: 1,
    available_quantity: 1,
    price: 0,
    description: ''
  }
}

const dialog = reactive({
  visible: false,
  isEdit: false,
  form: emptyForm()
})

const formRef = ref()
const rules = {
  title: [{ required: true, message: '请输入书名', trigger: 'blur' }],
  author: [{ required: true, message: '请输入作者', trigger: 'blur' }]
}

async function fetchList() {
  loading.value = true
  try {
    const { items, total: t } = await getBooksApi(query)
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
    const { items } = await getCategoriesApi()
    categories.value = items || []
  } catch (err) {
    categories.value = []
  }
}

function handleSearch() {
  query.page = 1
  fetchList()
}

function openCreate() {
  Object.assign(dialog.form, emptyForm())
  dialog.isEdit = false
  dialog.visible = true
}

function openEdit(row) {
  Object.assign(dialog.form, emptyForm(), row)
  dialog.isEdit = true
  dialog.visible = true
}

async function submit() {
  await formRef.value.validate()
  if (dialog.isEdit) {
    await updateBookApi(dialog.form.id, dialog.form)
    ElMessage.success('更新成功')
  } else {
    await createBookApi(dialog.form)
    ElMessage.success('新增成功')
  }
  dialog.visible = false
  fetchList()
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确认删除《${row.title}》?`, '提示', {
    type: 'warning'
  })
  await deleteBookApi(row.id)
  ElMessage.success('删除成功')
  fetchList()
}

onMounted(() => {
  fetchCategories()
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
            style="width: 220px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="'Search'" @click="handleSearch">
            查询
          </el-button>
          <el-button type="success" :icon="'Plus'" @click="openCreate">
            新增图书
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never">
      <el-table v-loading="loading" :data="list" border stripe>
        <el-table-column type="index" label="#" width="50" />
        <el-table-column prop="isbn" label="ISBN" width="140" />
        <el-table-column prop="title" label="书名" min-width="160" />
        <el-table-column prop="author" label="作者" width="110" />
        <el-table-column prop="publisher" label="出版社" width="150" />
        <el-table-column label="分类" width="100">
          <template #default="{ row }">
            {{ row.category?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="available_quantity" label="可借" width="70" align="center" />
        <el-table-column prop="total_quantity" label="总藏" width="70" align="center" />
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
      :title="dialog.isEdit ? '编辑图书' : '新增图书'"
      width="600px"
    >
      <el-form ref="formRef" :model="dialog.form" :rules="rules" label-width="90px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="书名" prop="title">
              <el-input v-model="dialog.form.title" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="作者" prop="author">
              <el-input v-model="dialog.form.author" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="ISBN">
              <el-input v-model="dialog.form.isbn" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分类">
              <el-select
                v-model="dialog.form.category_id"
                placeholder="请选择"
                clearable
                style="width: 100%"
              >
                <el-option
                  v-for="c in categories"
                  :key="c.id"
                  :label="c.name"
                  :value="c.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="出版社">
              <el-input v-model="dialog.form.publisher" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出版年份">
              <el-input-number
                v-model="dialog.form.publish_year"
                :min="0"
                :max="3000"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="馆藏位置">
              <el-input v-model="dialog.form.location" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="价格">
              <el-input-number
                v-model="dialog.form.price"
                :min="0"
                :precision="2"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="总馆藏">
              <el-input-number
                v-model="dialog.form.total_quantity"
                :min="0"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="可借库存">
              <el-input-number
                v-model="dialog.form.available_quantity"
                :min="0"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="简介">
          <el-input v-model="dialog.form.description" type="textarea" :rows="2" />
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
