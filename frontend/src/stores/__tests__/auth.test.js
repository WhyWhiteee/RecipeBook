import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../auth.js'

const axiosMock = vi.hoisted(() => {
  const mockPost = vi.fn()
  const instance = {
    post: mockPost,
    get: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() }
    }
  }
  return {
    mockPost,
    create: vi.fn(() => instance)
  }
})

vi.mock('axios', () => ({
  default: {
    create: axiosMock.create
  }
}))

describe('useAuthStore', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
    axiosMock.mockPost.mockReset()
  })

  it('initial state: isAuthenticated is false without token', () => {
    const store = useAuthStore()
    expect(store.isAuthenticated).toBe(false)
    expect(store.token).toBeNull()
    expect(store.user).toBeNull()
  })

  it('initial state: isAuthenticated is true when token exists in localStorage', () => {
    localStorage.setItem('token', 'existing-token')
    const store = useAuthStore()
    expect(store.isAuthenticated).toBe(true)
    expect(store.token).toBe('existing-token')
  })

  it('login: calls api.post, sets token, user, and localStorage', async () => {
    axiosMock.mockPost.mockResolvedValue({
      data: {
        token: 'abc123',
        user_id: 5,
        username: 'chef',
        email: 'chef@example.com'
      }
    })

    const store = useAuthStore()
    await store.login({ username: 'chef', password: 'secret' })

    expect(axiosMock.mockPost).toHaveBeenCalledWith('/auth/login/', {
      username: 'chef',
      password: 'secret'
    })
    expect(store.token).toBe('abc123')
    expect(store.user).toEqual({
      id: 5,
      username: 'chef',
      email: 'chef@example.com'
    })
    expect(localStorage.getItem('token')).toBe('abc123')
    expect(store.isAuthenticated).toBe(true)
  })

  it('login: returns API payload', async () => {
    const data = {
      token: 't1',
      user_id: 1,
      username: 'u1',
      email: 'u1@example.com'
    }
    axiosMock.mockPost.mockResolvedValue({ data })

    const store = useAuthStore()
    const result = await store.login({ username: 'u1', password: 'p' })

    expect(result).toEqual(data)
  })

  it('logout: clears token, user, and localStorage', () => {
    localStorage.setItem('token', 'abc123')
    const store = useAuthStore()
    store.user = { id: 1, username: 'x', email: 'x@example.com' }

    store.logout()

    expect(store.token).toBeNull()
    expect(store.user).toBeNull()
    expect(localStorage.getItem('token')).toBeNull()
    expect(store.isAuthenticated).toBe(false)
  })
})
