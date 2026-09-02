import client from './client'

// 管理员登录，返回 {access_token, user}
export const login = (username, password) =>
  client.post('/auth/login', { username, password })

// 获取当前登录用户
export const getCurrentUser = () => client.get('/auth/me')

// 注册新管理员（仅 super_admin）
export const register = (payload) => client.post('/auth/register', payload)
