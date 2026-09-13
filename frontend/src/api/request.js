import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 请求实例工厂:管理员端与学生端各自绑定 token key 与 401 跳转目标,会话互不干扰
function createRequest({ tokenKey, userKey, loginPath }) {
  const instance = axios.create({
    baseURL: '/api',
    timeout: 15000
  })

  // 请求拦截:自动携带对应端的 JWT
  instance.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem(tokenKey)
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    },
    (error) => Promise.reject(error)
  )

  // 响应拦截:解包后端 {code, msg, data} 信封,直接返回 data
  instance.interceptors.response.use(
    (response) => {
      const body = response.data
      if (body && typeof body === 'object' && 'code' in body) {
        if (body.code === 0) {
          return body.data
        }
        // 业务错误:统一提示并拒绝
        ElMessage.error(body.msg || '请求失败')
        return Promise.reject(new Error(body.msg || '请求失败'))
      }
      return body
    },
    (error) => {
      const status = error.response?.status
      const body = error.response?.data
      const message = body?.msg || error.message || '请求失败'

      if (status === 401) {
        localStorage.removeItem(tokenKey)
        localStorage.removeItem(userKey)
        ElMessage.error('登录已过期,请重新登录')
        router.push(loginPath)
      } else {
        ElMessage.error(message)
      }
      return Promise.reject(error)
    }
  )

  return instance
}

// 管理员端实例(默认导出,现有 api 模块不受影响)
const request = createRequest({
  tokenKey: 'admin_token',
  userKey: 'admin_user',
  loginPath: '/login'
})

// 学生端实例
export const studentRequest = createRequest({
  tokenKey: 'student_token',
  userKey: 'student_user',
  loginPath: '/student/login'
})

// 一次性清理旧版单一 token key
localStorage.removeItem('token')
localStorage.removeItem('user')

export default request
