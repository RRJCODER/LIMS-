import api from './client'

export const authApi = {
  login: (email: string, password: string) =>
    api.post('/api/v1/auth/login', { email, password }).then((r) => r.data),
  me: () => api.get('/api/v1/auth/me').then((r) => r.data),
  logout: () => api.post('/api/v1/auth/logout').then((r) => r.data),
}
