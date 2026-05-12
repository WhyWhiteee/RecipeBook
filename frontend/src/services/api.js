import axios from 'axios'
import { useToastStore } from '../stores/toast'
import { formatApiError } from '../utils/formatApiError'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  timeout: 10000
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Token ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status

    if (status === 401) {
      localStorage.removeItem('token')
      const publicPaths = ['/login', '/register']
      if (!publicPaths.includes(window.location.pathname)) {
        window.location.href = '/login'
      }
      return Promise.reject(error)
    }

    if (!error.config?.skipErrorToast) {
      try {
        useToastStore().push(formatApiError(error), 'danger')
      } catch (_) {
        /* Pinia ещё не готов */
      }
    }

    return Promise.reject(error)
  }
)

export default api
