import client from './client'

export const listReaders = (params = {}) =>
  client.get('/readers/', { params })

export const getReader = (id) => client.get(`/readers/${id}`)

export const createReader = (payload) => client.post('/readers/', payload)

export const updateReader = (id, payload) =>
  client.put(`/readers/${id}`, payload)

export const deleteReader = (id) => client.delete(`/readers/${id}`)
