import api from './client'

export const dashboardApi = {
  kpis: () => api.get('/api/v1/dashboard/kpis').then((r) => r.data),
  throughput: (days = 30) => api.get('/api/v1/dashboard/sample-throughput', { params: { days } }).then((r) => r.data),
}
