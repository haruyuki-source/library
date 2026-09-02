<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getCategoriesApi,
  createCategoryApi,
  updateCategoryApi,
  deleteCategoryApi
} from '@/api/category'

// 分类管理:列表 + 增删改
const loading = ref(false)
const list = ref([])

const dialog = reactive({
  visible: false,
  isEdit: false,
  form: { id: null, name: '', description: '' }
})

const formRef = ref()
const rules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }]
}

async function fetchList() {
  loading.value = true
  try {
    const { items } = await getCategoriesApi()
    list.value = items || []
  } catch (err) {
    list.value = []
  } finally {
    loading.value = false
  }
}

function resetForm() {
  Object.assign(dialog.form, { id: null, name: '', description: '' })
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
    await updateCategoryApi(dialog.form.id, dialog.form)
    ElMessage.success('更新成功')
  } else {
    await createCategoryApi(dialog.form)
    ElMessage.success('新增成功')
  }
  dialog.visible = false
  fetchList()
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确认删除分类「${row.name}」?`, '提示', {
    type: 'warning'
  })
  await deleteCategoryApi(row.id)
  ElMessage.success('删除成功')
  fetchList()
}

onMounted(fetchList)
</script>

<template>
  <div>
    <el-card shadow="never" class="toolbar">
      <el-button type="success" :icon="'Plus'" @click="openCreate">
        新增分类
      </el-button>
    </el-card>

    <el-card shadow="never">
      <el-table v-loading="loading" :data="list" border stripe>
        <el-table-column type="index" label="#" width="50" />
        <el-table-column prop="name" label="分类名称" min-width="180" />
        <el-table-column prop="description" label="描述" min-width="240" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialog.visible"
      :title="dialog.isEdit ? '编辑分类' : '新增分类'"
      width="480px"
    >
      <el-form ref="formRef" :model="dialog.form" :rules="rules" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="dialog.form.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="dialog.form.description" type="textarea" />
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
</style>
