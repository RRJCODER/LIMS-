import api from './client'

export const testsApi = {
  list: (status?: string) => api.get('/api/v1/tests/', { params: status ? { status_filter: status } : {} }).then((r) => r.data),
  get: (id: string) => api.get(`/api/v1/tests/${id}`).then((r) => r.data),
  create: (data: any) => api.post('/api/v1/tests/', data).then((r) => r.data),
  enterResults: (id: string, results: any[]) => api.post(`/api/v1/tests/${id}/results`, results).then((r) => r.data),
  approve: (id: string) => api.post(`/api/v1/tests/${id}/approve`).then((r) => r.data),
}
