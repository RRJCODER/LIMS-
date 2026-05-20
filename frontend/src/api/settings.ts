import api from './client'

export const settingsApi = {
  labProfile: () => api.get('/api/v1/settings/lab-profile').then((r) => r.data),
  updateLabProfile: (data: any) => api.put('/api/v1/settings/lab-profile', data).then((r) => r.data),
  uploadLogo: (file: File) => {
    const fd = new FormData()
    fd.append('file', file)
    return api.post('/api/v1/settings/lab-profile/logo', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then((r) => r.data)
  },
  qualityGrades: () => api.get('/api/v1/settings/quality-grades').then((r) => r.data),
  specifications: () => api.get('/api/v1/settings/specifications').then((r) => r.data),
  updateSpec: (analyteId: string, gradeId: string, data: any) =>
    api.put(`/api/v1/settings/specifications/${analyteId}/${gradeId}`, data).then((r) => r.data),
}
