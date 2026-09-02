import request from './request'

// 分类接口:增删改查
export const getCategoriesApi = (params) =>
  request.get('/categories', { params })
export const getCategoryApi = (id) => request.get(`/categories/${id}`)
export const createCategoryApi = (data) => request.post('/categories', data)
export const updateCategoryApi = (id, data) =>
  request.put(`/categories/${id}`, data)
export const deleteCategoryApi = (id) => request.delete(`/categories/${id}`)
