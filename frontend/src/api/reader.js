import request from './request'

// 读者接口:增删改查 + 分页
export const getReadersApi = (params) => request.get('/readers', { params })
export const getReaderApi = (id) => request.get(`/readers/${id}`)
export const createReaderApi = (data) => request.post('/readers', data)
export const updateReaderApi = (id, data) => request.put(`/readers/${id}`, data)
export const deleteReaderApi = (id) => request.delete(`/readers/${id}`)
