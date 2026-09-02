import client from './client'

export const listBooks = (params = {}) =>
  client.get('/books/', { params })

export const getBook = (id) => client.get(`/books/${id}`)

export const createBook = (payload) => client.post('/books/', payload)

export const updateBook = (id, payload) => client.put(`/books/${id}`, payload)

export const deleteBook = (id) => client.delete(`/books/${id}`)
