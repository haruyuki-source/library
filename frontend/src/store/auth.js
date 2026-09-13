import { defineStore } from 'pinia'
import { loginApi, getProfileApi } from '@/api/auth'

// 管理员端鉴权状态:token 持久化到 localStorage(与学生端 key 隔离)
export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('admin_token') || '',
    user: JSON.parse(localStorage.getItem('admin_user') || 'null')
  }),

  getters: {
    isLoggedIn: (state) => Boolean(state.token)
  },

  actions: {
    // 登录:保存 token 与用户信息(响应拦截器已解包,直接返回 data)
    async login(credentials) {
      const data = await loginApi(credentials)
      this.token = data.access_token
      this.user = data.user || null
      localStorage.setItem('admin_token', this.token)
      if (this.user) {
        localStorage.setItem('admin_user', JSON.stringify(this.user))
      }
      return data
    },

    // 拉取当前用户信息
    async fetchProfile() {
      if (!this.token) return null
      const data = await getProfileApi()
      this.user = data
      localStorage.setItem('admin_user', JSON.stringify(this.user))
      return data
    },

    // 登出:清空本地态
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_user')
    }
  }
})
