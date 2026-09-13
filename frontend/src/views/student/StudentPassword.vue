<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { updateStudentPasswordApi } from '@/api/student'
import { useStudentStore } from '@/store/student'

// 学生端修改密码:成功后强制下线,用新密码重新登录
const router = useRouter()
const student = useStudentStore()

const loading = ref(false)
const formRef = ref()
const form = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const rules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 128, message: '新密码长度 6-128 位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== form.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

async function handleSubmit() {
  await formRef.value.validate()
  loading.value = true
  try {
    await updateStudentPasswordApi({
      old_password: form.old_password,
      new_password: form.new_password
    })
    ElMessage.success('密码修改成功,请重新登录')
    // JWT 无状态,旧 token 在有效期内仍可用,前端强制下线兜底
    student.logout()
    router.push('/student/login')
  } catch (err) {
    // 错误已由 request 拦截器统一提示
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <el-card shadow="never" class="pwd-card">
    <template #header>
      <span class="card-title">修改密码</span>
    </template>
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="90px"
      @keyup.enter="handleSubmit"
    >
      <el-form-item label="原密码" prop="old_password">
        <el-input
          v-model="form.old_password"
          type="password"
          show-password
          placeholder="请输入原密码"
        />
      </el-form-item>
      <el-form-item label="新密码" prop="new_password">
        <el-input
          v-model="form.new_password"
          type="password"
          show-password
          placeholder="至少 6 位"
        />
      </el-form-item>
      <el-form-item label="确认密码" prop="confirm_password">
        <el-input
          v-model="form.confirm_password"
          type="password"
          show-password
          placeholder="请再次输入新密码"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="loading" @click="handleSubmit">
          保存
        </el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<style scoped>
.pwd-card {
  max-width: 520px;
}
.card-title {
  color: #880e4f;
  font-weight: 600;
}
</style>
