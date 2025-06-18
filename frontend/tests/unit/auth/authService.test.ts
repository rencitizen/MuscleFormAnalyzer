/**
 * Authentication Service Unit Tests
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { authService } from '@/lib/services/authService'

// Mock fetch
global.fetch = vi.fn()

describe('Authentication Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  describe('login', () => {
    it('should successfully login user', async () => {
      const mockResponse = {
        ok: true,
        json: async () => ({
          user: {
            id: 'test-id',
            email: 'test@example.com',
            name: 'Test User'
          },
          token: 'mock-jwt-token'
        })
      }

      vi.mocked(fetch).mockResolvedValueOnce(mockResponse as any)

      const result = await authService.login('test@example.com', 'password123')
      
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/auth/login'),
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            email: 'test@example.com',
            password: 'password123'
          })
        })
      )

      expect(result.user.email).toBe('test@example.com')
      expect(result.token).toBe('mock-jwt-token')
    })

    it('should handle login failure', async () => {
      const mockResponse = {
        ok: false,
        status: 401,
        json: async () => ({
          error: 'Invalid credentials'
        })
      }

      vi.mocked(fetch).mockResolvedValueOnce(mockResponse as any)

      await expect(authService.login('test@example.com', 'wrong-password'))
        .rejects.toThrow('Invalid credentials')
    })
  })

  describe('register', () => {
    it('should successfully register new user', async () => {
      const mockResponse = {
        ok: true,
        json: async () => ({
          user: {
            id: 'new-user-id',
            email: 'newuser@example.com',
            name: 'New User'
          },
          token: 'new-user-token'
        })
      }

      vi.mocked(fetch).mockResolvedValueOnce(mockResponse as any)

      const result = await authService.register({
        email: 'newuser@example.com',
        password: 'password123',
        name: 'New User'
      })

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/auth/register'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            email: 'newuser@example.com',
            password: 'password123',
            name: 'New User'
          })
        })
      )

      expect(result.user.email).toBe('newuser@example.com')
    })

    it('should validate registration data', async () => {
      // Test invalid email
      await expect(authService.register({
        email: 'invalid-email',
        password: 'password123',
        name: 'Test User'
      })).rejects.toThrow()

      // Test weak password
      await expect(authService.register({
        email: 'test@example.com',
        password: '123',
        name: 'Test User'
      })).rejects.toThrow()
    })
  })

  describe('logout', () => {
    it('should clear user session', async () => {
      // Set up initial session
      localStorage.setItem('auth_token', 'test-token')
      localStorage.setItem('user', JSON.stringify({ id: 'test-id' }))

      const mockResponse = {
        ok: true,
        json: async () => ({ success: true })
      }

      vi.mocked(fetch).mockResolvedValueOnce(mockResponse as any)

      await authService.logout()

      expect(localStorage.getItem('auth_token')).toBeNull()
      expect(localStorage.getItem('user')).toBeNull()
    })
  })

  describe('getCurrentUser', () => {
    it('should return current user from token', async () => {
      const mockToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6InRlc3QtaWQiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20ifQ.signature'
      localStorage.setItem('auth_token', mockToken)

      const mockResponse = {
        ok: true,
        json: async () => ({
          user: {
            id: 'test-id',
            email: 'test@example.com',
            name: 'Test User'
          }
        })
      }

      vi.mocked(fetch).mockResolvedValueOnce(mockResponse as any)

      const user = await authService.getCurrentUser()
      
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/auth/me'),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': `Bearer ${mockToken}`
          })
        })
      )

      expect(user?.email).toBe('test@example.com')
    })

    it('should return null when no token', async () => {
      const user = await authService.getCurrentUser()
      expect(user).toBeNull()
    })
  })

  describe('refreshToken', () => {
    it('should refresh expired token', async () => {
      const oldToken = 'old-token'
      const newToken = 'new-token'
      
      localStorage.setItem('auth_token', oldToken)
      localStorage.setItem('refresh_token', 'refresh-token')

      const mockResponse = {
        ok: true,
        json: async () => ({
          token: newToken,
          refreshToken: 'new-refresh-token'
        })
      }

      vi.mocked(fetch).mockResolvedValueOnce(mockResponse as any)

      const result = await authService.refreshToken()

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/auth/refresh'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            refreshToken: 'refresh-token'
          })
        })
      )

      expect(result.token).toBe(newToken)
      expect(localStorage.getItem('auth_token')).toBe(newToken)
    })
  })

  describe('validateToken', () => {
    it('should validate token format', () => {
      const validToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6InRlc3QtaWQifQ.signature'
      const invalidToken = 'invalid-token'

      expect(authService.isValidToken(validToken)).toBe(true)
      expect(authService.isValidToken(invalidToken)).toBe(false)
    })

    it('should check token expiration', () => {
      const expiredToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6InRlc3QtaWQiLCJleHAiOjE2MDAwMDAwMDB9.signature'
      const validToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6InRlc3QtaWQiLCJleHAiOjk5OTk5OTk5OTl9.signature'

      expect(authService.isTokenExpired(expiredToken)).toBe(true)
      expect(authService.isTokenExpired(validToken)).toBe(false)
    })
  })
})