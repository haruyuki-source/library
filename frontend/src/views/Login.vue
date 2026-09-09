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
  /* 纯淡粉渐变 */
  background: linear-gradient(135deg, #fef4f7 0%, #fce4ec 50%, #f8bbd0 100%);
}

.login-card {
  width: 400px;
  padding: 24px 18px;
  border-radius: 16px;
  border: none;
  box-shadow: 0 12px 32px rgba(236, 107, 154, 0.18);
  /* 统一渐变,与全站卡片一致 */
  background: var(--card-gradient);
  backdrop-filter: blur(8px);
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
  color: #880e4f;
  letter-spacing: 1px;
}

.submit {
  width: 100%;
}
</style>
