import request from './request'

// 借阅接口:借书、还书、记录查询
export const getBorrowsApi = (params) => request.get('/borrows', { params })
export const borrowBookApi = (data) => request.post('/borrows', data)
export const returnBookApi = (id, data) =>
  request.put(`/borrows/${id}/return`, data)
export const deleteBorrowApi = (id) => request.delete(`/borrows/${id}`)
