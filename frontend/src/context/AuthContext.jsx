import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import * as authApi from '../api/auth'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // 初始化：从 localStorage 恢复 token + 用户
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    const saved = localStorage.getItem('user_info')
    if (!token) {
      setLoading(false)
      return
    }
    if (saved) {
      try {
        setUser(JSON.parse(saved))
      } catch {
        localStorage.removeItem('user_info')
      }
    }
    // 后台校验 token 有效性
    authApi
      .getCurrentUser()
      .then((data) => {
        setUser(data)
        localStorage.setItem('user_info', JSON.stringify(data))
      })
      .catch(() => {
        logout()
      })
      .finally(() => setLoading(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const login = useCallback(async (username, password) => {
    const data = await authApi.login(username, password)
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('user_info', JSON.stringify(data.user))
    setUser(data.user)
    return data.user
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_info')
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
