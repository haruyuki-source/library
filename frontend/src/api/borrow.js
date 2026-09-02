import client from './client'

// 借阅记录列表（分页 + 筛选）
export const listBorrowRecords = (params = {}) =>
  client.get('/borrow/', { params })

// 获取单条借阅记录
export const getBorrowRecord = (id) => client.get(`/borrow/${id}`)

// 获取指定读者的全部借阅记录
export const listBorrowByReader = (readerId) =>
  client.get(`/borrow/reader/${readerId}`)

// 获取当前逾期未还记录
export const listOverdue = () => client.get('/borrow/overdue')

// 借书
export const borrowBook = (payload) => client.post('/borrow/', payload)

// 还书
export const returnBook = (recordId, remark) =>
  client.post('/borrow/return', { record_id: recordId, remark })

// 续借
export const renewBook = (recordId, extraDays = 30) =>
  client.post('/borrow/renew', { record_id: recordId, extra_days: extraDays })
