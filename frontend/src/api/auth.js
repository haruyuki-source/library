import request from './request'

// 鉴权接口:登录、当前用户
export const loginApi = (data) => request.post('/auth/login', data)
export const getProfileApi = () => request.get('/auth/profile')
