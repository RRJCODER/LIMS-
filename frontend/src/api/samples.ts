import api from './client'

export const samplesApi = {
  list: (status?: string) => api.get('/api/v1/samples/', { params: status ? { status_filter: status } : {} }).then((r) => r.data),
  get: (id: string) => api.get(`/api/v1/samples/${id}`).then((r) => r.data),
  create: (data: any) => api.post('/api/v1/samples/', data).then((r) => r.data),
  updateStatus: (id: string, status: string, notes?: string) =>
    api.patch(`/api/v1/samples/${id}/status`, { status, notes }).then((r) => r.data),
  getCustody: (id: string) => api.get(`/api/v1/samples/${id}/custody`).then((r) => r.data),
  uploadAttachment: (id: string, file: File, fileType: string) => {
    const fd = new FormData()
    fd.append('file', file)
    fd.append('file_type', fileType)
    return api.post(`/api/v1/samples/${id}/attachments`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then((r) => r.data)
  },
}
