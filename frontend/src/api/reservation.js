import request from './request'

// 预约管理:列表 / 到馆确认借书(转借阅并扣库存) / 取消预约
export const getReservationsApi = (params) => request.get('/reservations', { params })
export const fulfillReservationApi = (id) => request.put(`/reservations/${id}/fulfill`)
export const cancelReservationAdminApi = (id) => request.put(`/reservations/${id}/cancel`)
