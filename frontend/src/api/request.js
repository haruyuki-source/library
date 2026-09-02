import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// Axios 实例:统一 baseURL、超时、请求/响应拦截
const request = axios.create({
  baseURL: '/api',
  timeout: 15000
})

// 请求拦截:自动携带 JWT
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截:解包后端 {code, msg, data} 信封,直接返回 data
request.interceptors.response.use(
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
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      ElMessage.error('登录已过期,请重新登录')
      router.push('/login')
    } else {
      ElMessage.error(message)
    }
    return Promise.reject(error)
  }
)

export default request
