import { studentRequest } from './request'

// 学生端接口:登录、个人信息、修改密码、我的借阅、在借图书、预约索书、忘记密码
export const studentLoginApi = (data) => studentRequest.post('/student/login', data)
export const forgotPasswordApi = (data) => studentRequest.post('/student/forgot-password', data)
export const getStudentProfileApi = () => studentRequest.get('/student/profile')
export const updateStudentPasswordApi = (data) => studentRequest.put('/student/password', data)
export const getStudentBorrowsApi = (params) => studentRequest.get('/student/borrows', { params })
export const getStudentActiveBorrowsApi = () => studentRequest.get('/student/borrows/active')

// 预约索书:登记预约(不扣库存)/ 我的预约 / 取消预约
export const getStudentReservationsApi = (params) =>
  studentRequest.get('/student/reservations', { params })
export const reserveBookApi = (bookId) =>
  studentRequest.post('/student/reservations', { book_id: bookId })
export const cancelReservationApi = (id) =>
  studentRequest.post(`/student/reservations/${id}/cancel`)
