import client from './client'

export const listCategories = (params = {}) =>
  client.get('/categories/', { params })

export const getCategory = (id) => client.get(`/categories/${id}`)

export const createCategory = (payload) => client.post('/categories/', payload)

export const updateCategory = (id, payload) =>
  client.put(`/categories/${id}`, payload)

export const deleteCategory = (id) => client.delete(`/categories/${id}`)
