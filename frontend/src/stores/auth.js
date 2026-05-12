import { defineStore } from 'pinia'
import api from '../services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: null
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token)
  },
  actions: {
    async login(payload) {
      const { data } = await api.post('/auth/login/', payload)
      this.token = data.token
      this.user = {
        id: data.user_id,
        username: data.username,
        email: data.email
      }
      localStorage.setItem('token', data.token)
      return data
    },
    async register(payload) {
      const { data } = await api.post('/auth/register/', payload)
      this.token = data.token
      this.user = {
        id: data.user_id,
        username: data.username,
        email: data.email
      }
      localStorage.setItem('token', data.token)
      return data
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
    }
  }
})
