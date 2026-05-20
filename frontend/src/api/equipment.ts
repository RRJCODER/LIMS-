import api from './client'

export const equipmentApi = {
  list: () => api.get('/api/v1/equipment/').then((r) => r.data),
  get: (id: string) => api.get(`/api/v1/equipment/${id}`).then((r) => r.data),
  create: (data: any) => api.post('/api/v1/equipment/', data).then((r) => r.data),
  dueCal: (days?: number) => api.get('/api/v1/equipment/due-calibration', { params: { days_ahead: days } }).then((r) => r.data),
  calibrations: (id: string) => api.get(`/api/v1/equipment/${id}/calibrations`).then((r) => r.data),
  addCalibration: (id: string, data: any) => api.post(`/api/v1/equipment/${id}/calibrations`, data).then((r) => r.data),
}
