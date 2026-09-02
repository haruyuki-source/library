import axios from 'axios'
import { message } from 'antd'

const client = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

// 请求拦截：附加 JWT
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 响应拦截：后端统一返回 {code, msg, data}
client.interceptors.response.use(
  (response) => {
    const { code, msg, data } = response.data || {}
    if (code === 200 || code === 201) return data
    message.error(msg || '请求失败')
    return Promise.reject(new Error(msg || '请求失败'))
  },
  (error) => {
    const resp = error.response
    if (resp) {
      const { code, msg } = resp.data || {}
      if (code === 401) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('user_info')
        message.error('登录已过期，请重新登录')
        if (location.pathname !== '/login') location.href = '/login'
      } else {
        message.error(msg || `请求失败（${resp.status}）`)
      }
    } else {
      message.error('网络异常，请稍后重试')
    }
    return Promise.reject(error)
  }
)

export default client
