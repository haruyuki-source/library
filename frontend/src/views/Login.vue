<script setup>
import { ref, reactive, watch, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/store/auth'
import { useStudentStore } from '@/store/student'
import { forgotPasswordApi } from '@/api/student'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const student = useStudentStore()

const activeTab = ref('admin')
const loading = ref(false)
const adminFormRef = ref()
const studentFormRef = ref()

const adminForm = reactive({
  username: '',
  password: ''
})

const studentForm = reactive({
  card_no: '',
  password: ''
})

const adminRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const studentRules = {
  card_no: [{ required: true, message: '请输入借书证号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function handleLogin() {
  if (activeTab.value === 'admin') {
    await adminFormRef.value.validate()
    loading.value = true
    try {
      await auth.login(adminForm)
      ElMessage.success('登录成功')
      router.push(route.query.redirect || '/')
    } catch (err) {
      // 错误已由 request 拦截器统一提示
    } finally {
      loading.value = false
    }
  } else {
    await studentFormRef.value.validate()
    loading.value = true
    try {
      await student.login(studentForm)
      ElMessage.success('登录成功')
      router.push(route.query.redirect || '/student/books')
    } catch (err) {
      // 错误已由 request 拦截器统一提示
    } finally {
      loading.value = false
    }
  }
}

// ---------- 忘记密码 ----------
const forgotVisible = ref(false)
const forgotLoading = ref(false)
const forgotFormRef = ref()
const forgotForm = reactive({
  card_no: '',
  phone: '',
  new_password: '',
  confirm_password: ''
})

const forgotRules = {
  card_no: [{ required: true, message: '请输入借书证号', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入预留手机号', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 128, message: '新密码长度 6-128 位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== forgotForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

function openForgot() {
  Object.assign(forgotForm, {
    card_no: '',
    phone: '',
    new_password: '',
    confirm_password: ''
  })
  // 清除上次兜底留下的强制隐藏态(v-show 随后也会自行恢复 display)
  document.querySelectorAll('.el-overlay[data-fb-hidden]').forEach((el) => {
    delete el.dataset.fbHidden
    el.style.display = ''
  })
  forgotVisible.value = true
}

// 兜底:个别环境(无头浏览器、被节流的后台标签页)不触发 requestAnimationFrame,
// 而 Vue 过渡依赖 rAF 收尾,遮罩会永久卡在 dialog-fade 过渡态无法移除。
// 关闭动画(0.3s)结束后若过渡类仍残留,则强制清理并隐藏;正常浏览器动画已结束,不会命中。
const STUCK_TRANSITION_RE = /dialog-fade-(?:enter|leave)-(?:from|active|to)/
const TRANSITION_CLASSES = [
  'dialog-fade-enter-from',
  'dialog-fade-enter-active',
  'dialog-fade-enter-to',
  'dialog-fade-leave-from',
  'dialog-fade-leave-active',
  'dialog-fade-leave-to'
]
function forceHideStuckOverlays() {
  document.querySelectorAll('.el-overlay').forEach((el) => {
    const stuck = STUCK_TRANSITION_RE.test(el.className)
    // 第二遍兜底:类名可能已被晚到的动画事件清掉、但遮罩又被恢复显示
    const restored = el.dataset.fbHidden === '1' && el.style.display !== 'none'
    if (!stuck && !restored) return
    el.classList.remove(...TRANSITION_CLASSES)
    // 模拟 v-show 关闭态;下次打开时由 openForgot / v-show 恢复
    el.dataset.fbHidden = '1'
    el.style.display = 'none'
  })
}

// 兜底:个别环境(无头浏览器、被节流的后台标签页)不触发 requestAnimationFrame,
// 而 Vue 过渡依赖 rAF 收尾,遮罩会卡在 dialog-fade 过渡态无法移除;
// 甚至晚到的动画事件还可能把已隐藏的遮罩恢复成可点击的透明层。
// 关闭动画(0.3s)结束后做两次强制收尾;正常浏览器动画早已结束,不会命中。
const fallbackTimers = []
watch(forgotVisible, (visible) => {
  if (visible) return
  ;[350, 900].forEach((delay) => {
    const timer = setTimeout(() => {
      // 期间又重新打开对话框则跳过
      if (forgotVisible.value) return
      forceHideStuckOverlays()
    }, delay)
    fallbackTimers.push(timer)
  })
})
onBeforeUnmount(() => fallbackTimers.forEach(clearTimeout))

async function handleForgot() {
  // validate() 校验失败会 reject,必须包在 try/catch 内,否则抛出未捕获异常
  try {
    await forgotFormRef.value.validate()
  } catch (err) {
    return
  }
  forgotLoading.value = true
  try {
    await forgotPasswordApi({
      card_no: forgotForm.card_no,
      phone: forgotForm.phone,
      new_password: forgotForm.new_password
    })
    // 先关闭对话框并提示
    forgotVisible.value = false
    ElMessage.success('密码重置成功,请使用新密码登录')
    // 回填与 tab 切换延迟到关闭动画(0.3s)结束后,避免对话框还在关闭时切走界面
    const cardNo = forgotForm.card_no
    setTimeout(() => {
      studentForm.card_no = cardNo
      studentForm.password = ''
      activeTab.value = 'student'
    }, 320)
  } catch (err) {
    // 错误已由 request 拦截器统一提示
  } finally {
    forgotLoading.value = false
  }
}
</script>

<template>
  <div class="login">
    <el-card class="login-card">
      <h2 class="title">图书馆管理系统</h2>
      <el-tabs v-model="activeTab" stretch class="login-tabs">
        <el-tab-pane label="管理员" name="admin">
          <el-form
            ref="adminFormRef"
            :model="adminForm"
            :rules="adminRules"
            label-position="top"
            @keyup.enter="handleLogin"
          >
            <el-form-item label="用户名" prop="username">
              <el-input
                v-model="adminForm.username"
                placeholder="请输入用户名"
                :prefix-icon="'User'"
              />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input
                v-model="adminForm.password"
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
        </el-tab-pane>
        <el-tab-pane label="学生" name="student">
          <el-form
            ref="studentFormRef"
            :model="studentForm"
            :rules="studentRules"
            label-position="top"
            @keyup.enter="handleLogin"
          >
            <el-form-item label="借书证号" prop="card_no">
              <el-input
                v-model="studentForm.card_no"
                placeholder="请输入借书证号"
                :prefix-icon="'Postcard'"
              />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input
                v-model="studentForm.password"
                type="password"
                show-password
                placeholder="初始密码为借书证号"
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
            <div class="forgot-link">
              <el-button link type="primary" @click="openForgot">
                忘记密码?
              </el-button>
            </div>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 忘记密码:借书证号 + 预留手机号 校验后重置 -->
    <el-dialog
      v-model="forgotVisible"
      title="找回密码"
      width="420px"
      append-to-body
    >
      <el-alert
        type="info"
        :closable="false"
        show-icon
        title="请输入借书证号与预留手机号,校验通过后可设置新密码;若手机号未登记请联系管理员重置。"
        class="forgot-tip"
      />
      <el-form
        ref="forgotFormRef"
        :model="forgotForm"
        :rules="forgotRules"
        label-width="84px"
      >
        <el-form-item label="借书证号" prop="card_no">
          <el-input v-model="forgotForm.card_no" placeholder="请输入借书证号" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="forgotForm.phone" placeholder="请输入预留手机号" />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="forgotForm.new_password"
            type="password"
            show-password
            placeholder="至少 6 位"
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input
            v-model="forgotForm.confirm_password"
            type="password"
            show-password
            placeholder="请再次输入新密码"
            @keyup.enter="handleForgot"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="forgotVisible = false">取消</el-button>
        <el-button type="primary" :loading="forgotLoading" @click="handleForgot">
          重置密码
        </el-button>
      </template>
    </el-dialog>
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
  margin: 0 0 16px;
  color: #880e4f;
  letter-spacing: 1px;
}

.submit {
  width: 100%;
}

.forgot-link {
  margin-top: 8px;
  text-align: right;
}

.forgot-tip {
  margin-bottom: 16px;
}
</style>
