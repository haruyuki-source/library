import { defineStore } from 'pinia'
import { loginApi, getProfileApi } from '@/api/auth'

// 鉴权状态:token 持久化到 localStorage,用户信息懒加载
export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null')
  }),

  getters: {
    isLoggedIn: (state) => Boolean(state.token)
  },

  actions: {
    // 登录:保存 token 与用户信息
    async login(credentials) {
      const { data } = await loginApi(credentials)
      this.token = data.access_token
      this.user = data.user || null
      localStorage.setItem('token', this.token)
      if (this.user) {
        localStorage.setItem('user', JSON.stringify(this.user))
      }
      return data
    },

    // 拉取当前用户信息
    async fetchProfile() {
      if (!this.token) return null
      const { data } = await getProfileApi()
      this.user = data
      localStorage.setItem('user', JSON.stringify(this.user))
      return data
    },

    // 登出:清空本地态
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})
