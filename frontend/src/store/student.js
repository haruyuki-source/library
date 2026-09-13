import { defineStore } from 'pinia'
import { studentLoginApi, getStudentProfileApi } from '@/api/student'

// 学生端鉴权状态:token 持久化到 localStorage(与管理员端 key 隔离)
export const useStudentStore = defineStore('student', {
  state: () => ({
    token: localStorage.getItem('student_token') || '',
    user: JSON.parse(localStorage.getItem('student_user') || 'null')
  }),

  getters: {
    isLoggedIn: (state) => Boolean(state.token)
  },

  actions: {
    // 登录:保存 token 与用户信息(响应拦截器已解包,直接返回 data)
    async login(credentials) {
      const data = await studentLoginApi(credentials)
      this.token = data.access_token
      this.user = data.user || null
      localStorage.setItem('student_token', this.token)
      if (this.user) {
        localStorage.setItem('student_user', JSON.stringify(this.user))
      }
      return data
    },

    // 拉取当前学生信息
    async fetchProfile() {
      if (!this.token) return null
      const data = await getStudentProfileApi()
      this.user = data
      localStorage.setItem('student_user', JSON.stringify(this.user))
      return data
    },

    // 登出:清空本地态
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('student_token')
      localStorage.removeItem('student_user')
    }
  }
})
