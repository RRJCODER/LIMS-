import api from './client'

export const qcApi = {
  charts: () => api.get('/api/v1/qc/charts').then((r) => r.data),
  chartData: (id: string) => api.get(`/api/v1/qc/charts/${id}/data`).then((r) => r.data),
  violations: (resolved?: boolean) =>
    api.get('/api/v1/qc/violations', { params: resolved !== undefined ? { resolved } : {} }).then((r) => r.data),
  summary: () => api.get('/api/v1/qc/summary').then((r) => r.data),
}
