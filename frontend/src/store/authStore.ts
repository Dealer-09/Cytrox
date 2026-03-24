import { create } from 'zustand'
import api from '../api/client'

interface User {
  id: number
  username: string
  email: string
  avatar_url: string
  subscription_tier: string
}

interface AuthStore {
  user: User | null
  isAuthenticated: boolean
  login: (code: string) => Promise<void>
  logout: () => void
  checkAuth: () => Promise<void>
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  isAuthenticated: false,

  login: async (code: string) => {
    try {
      const response = await api.post('/auth/github/callback', { code })
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('refresh_token', response.data.refresh_token)
      set({
        user: response.data.user,
        isAuthenticated: true,
      })
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    set({ user: null, isAuthenticated: false })
  },

  checkAuth: async () => {
    const token = localStorage.getItem('access_token')
    if (token) {
      try {
        const response = await api.get('/auth/me')
        set({ user: response.data, isAuthenticated: true })
      } catch (error) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        set({ user: null, isAuthenticated: false })
      }
    }
  },
}))
