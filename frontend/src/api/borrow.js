import request from './request'

// 借阅接口:借书、还书、续借、记录查询
// 注意:后端蓝图注册在 /api/borrow(单数)
export const getBorrowsApi = (params) => request.get('/borrow', { params })
export const borrowBookApi = (data) => request.post('/borrow', data)
export const returnBookApi = (id, data) =>
  request.put(`/borrow/${id}/return`, data)
export const renewBookApi = (id, data) => request.put(`/borrow/${id}/renew`, data)
export const deleteBorrowApi = (id) => request.delete(`/borrow/${id}`)
