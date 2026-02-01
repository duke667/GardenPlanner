import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Plants
export const plantAPI = {
  getAll: (params) => api.get('/plants/', { params }),
  get: (id) => api.get(`/plants/${id}/`),
  create: (data) => api.post('/plants/', data),
  update: (id, data) => api.put(`/plants/${id}/`, data),
  delete: (id) => api.delete(`/plants/${id}/`),
  getCycles: (id) => api.get(`/plants/${id}/cycles_detail/`)
}

// Planting Cycles
export const cycleAPI = {
  getAll: (params) => api.get('/cycles/', { params }),
  get: (id) => api.get(`/cycles/${id}/`),
  create: (data) => api.post('/cycles/', data),
  update: (id, data) => api.put(`/cycles/${id}/`, data),
  delete: (id) => api.delete(`/cycles/${id}/`),
  addEvent: (id, data) => api.post(`/cycles/${id}/add_event/`, data),
  addTask: (id, data) => api.post(`/cycles/${id}/add_task/`, data)
}

// Events
export const eventAPI = {
  getAll: (params) => api.get('/events/', { params }),
  get: (id) => api.get(`/events/${id}/`),
  create: (data) => api.post('/events/', data),
  update: (id, data) => api.put(`/events/${id}/`, data),
  delete: (id) => api.delete(`/events/${id}/`)
}

// Tasks
export const taskAPI = {
  getAll: (params) => api.get('/tasks/', { params }),
  get: (id) => api.get(`/tasks/${id}/`),
  create: (data) => api.post('/tasks/', data),
  update: (id, data) => api.put(`/tasks/${id}/`, data),
  delete: (id) => api.delete(`/tasks/${id}/`),
  toggleComplete: (id) => api.post(`/tasks/${id}/toggle_complete/`)
}

// Dashboard
export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats/')
}

export default api
