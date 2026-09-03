<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const loading = ref(false)
const formRef = ref()
const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function handleLogin() {
  await formRef.value.validate()
  loading.value = true
  try {
    await auth.login(form)
    ElMessage.success('登录成功')
    router.push(route.query.redirect || '/')
  } catch (err) {
    // 错误已由 request 拦截器统一提示
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login">
    <el-card class="login-card">
      <h2 class="title">图书馆管理系统</h2>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        @keyup.enter="handleLogin"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            :prefix-icon="'User'"
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            show-password
            placeholder="请输入密码"
            :prefix-icon="'Lock'"
          />
        </el-form-item>
        <el-button
          type="primary"
          class="submit"
          :loading="loading"
          @click="handleLogin"
        >
          登 录
        </el-button>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.login {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
}

.login-card {
  width: 400px;
  padding: 20px 10px;
}

@media (max-width: 480px) {
  .login-card {
    width: calc(100vw - 32px);
    padding: 16px 12px;
    border-radius: 10px;
  }
  .title {
    font-size: 20px;
  }
}

.title {
  text-align: center;
  margin: 0 0 24px;
  color: #303133;
}

.submit {
  width: 100%;
}
</style>
