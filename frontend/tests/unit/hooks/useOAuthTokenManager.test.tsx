import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useOAuthTokenManager } from '@/hooks/useOAuthTokenManager';

// Mock timers
vi.useFakeTimers();

// Mock fetch
global.fetch = vi.fn();

describe('useOAuthTokenManager', () => {
  const mockTokens = {
    access_token: 'test-access-token',
    refresh_token: 'test-refresh-token',
    expires_in: 3600,
    token_type: 'Bearer'
  };

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    
    // Mock environment variables
    process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID = 'test-client-id';
  });

  afterEach(() => {
    vi.clearAllTimers();
  });

  describe('initialization', () => {
    it('should initialize with null tokens', () => {
      const { result } = renderHook(() => useOAuthTokenManager());

      expect(result.current.tokens).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.isLoading).toBe(false);
    });

    it('should load tokens from localStorage on mount', () => {
      const storedTokens = {
        ...mockTokens,
        expires_at: Date.now() + 3600000
      };
      localStorage.setItem('oauth_tokens', JSON.stringify(storedTokens));

      const { result } = renderHook(() => useOAuthTokenManager());

      expect(result.current.tokens).toEqual(storedTokens);
      expect(result.current.isAuthenticated).toBe(true);
    });

    it('should clear expired tokens from localStorage', () => {
      const expiredTokens = {
        ...mockTokens,
        expires_at: Date.now() - 1000 // Expired 1 second ago
      };
      localStorage.setItem('oauth_tokens', JSON.stringify(expiredTokens));

      const { result } = renderHook(() => useOAuthTokenManager());

      expect(result.current.tokens).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(localStorage.getItem('oauth_tokens')).toBeNull();
    });
  });

  describe('setTokens', () => {
    it('should store tokens with calculated expiry time', () => {
      const { result } = renderHook(() => useOAuthTokenManager());

      act(() => {
        result.current.setTokens(mockTokens);
      });

      expect(result.current.tokens).toMatchObject({
        ...mockTokens,
        expires_at: expect.any(Number)
      });
      expect(result.current.isAuthenticated).toBe(true);

      const storedTokens = JSON.parse(localStorage.getItem('oauth_tokens') || '{}');
      expect(storedTokens).toMatchObject({
        ...mockTokens,
        expires_at: expect.any(Number)
      });
    });

    it('should set up auto-refresh timer', () => {
      const { result } = renderHook(() => useOAuthTokenManager());

      act(() => {
        result.current.setTokens(mockTokens);
      });

      // Fast-forward to 5 minutes before expiry
      act(() => {
        vi.advanceTimersByTime((3600 - 300) * 1000);
      });

      // Verify refresh was attempted
      expect(fetch).toHaveBeenCalledWith(
        'https://oauth2.googleapis.com/token',
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('refresh_token=test-refresh-token')
        })
      );
    });
  });

  describe('clearTokens', () => {
    it('should clear tokens from state and localStorage', () => {
      const { result } = renderHook(() => useOAuthTokenManager());

      act(() => {
        result.current.setTokens(mockTokens);
      });

      expect(result.current.isAuthenticated).toBe(true);

      act(() => {
        result.current.clearTokens();
      });

      expect(result.current.tokens).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(localStorage.getItem('oauth_tokens')).toBeNull();
    });

    it('should cancel auto-refresh timer', () => {
      const { result } = renderHook(() => useOAuthTokenManager());

      act(() => {
        result.current.setTokens(mockTokens);
      });

      act(() => {
        result.current.clearTokens();
      });

      // Fast-forward past refresh time
      act(() => {
        vi.advanceTimersByTime(3600 * 1000);
      });

      // Verify refresh was NOT attempted after clearing
      expect(fetch).not.toHaveBeenCalled();
    });
  });

  describe('refreshTokens', () => {
    it('should refresh tokens successfully', async () => {
      const newTokens = {
        access_token: 'new-access-token',
        expires_in: 3600,
        token_type: 'Bearer'
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => newTokens
      });

      const { result } = renderHook(() => useOAuthTokenManager());

      act(() => {
        result.current.setTokens(mockTokens);
      });

      await act(async () => {
        await result.current.refreshTokens();
      });

      expect(result.current.tokens?.access_token).toBe('new-access-token');
      expect(result.current.tokens?.refresh_token).toBe('test-refresh-token'); // Preserved
      expect(result.current.isAuthenticated).toBe(true);
    });

    it('should handle refresh failure', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 401,
        text: async () => 'Invalid refresh token'
      });

      const { result } = renderHook(() => useOAuthTokenManager());

      act(() => {
        result.current.setTokens(mockTokens);
      });

      await act(async () => {
        await result.current.refreshTokens();
      });

      expect(result.current.tokens).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(localStorage.getItem('oauth_tokens')).toBeNull();
    });

    it('should not refresh if no refresh token', async () => {
      const tokensWithoutRefresh = {
        access_token: 'test-access-token',
        expires_in: 3600,
        token_type: 'Bearer'
      };

      const { result } = renderHook(() => useOAuthTokenManager());

      act(() => {
        result.current.setTokens(tokensWithoutRefresh);
      });

      await act(async () => {
        await result.current.refreshTokens();
      });

      expect(fetch).not.toHaveBeenCalled();
    });
  });

  describe('getValidAccessToken', () => {
    it('should return access token if not expired', async () => {
      const { result } = renderHook(() => useOAuthTokenManager());

      act(() => {
        result.current.setTokens(mockTokens);
      });

      const token = await act(async () => {
        return await result.current.getValidAccessToken();
      });

      expect(token).toBe('test-access-token');
      expect(fetch).not.toHaveBeenCalled();
    });

    it('should refresh and return new token if expired', async () => {
      const expiredTokens = {
        ...mockTokens,
        expires_at: Date.now() - 1000 // Expired
      };

      const newTokens = {
        access_token: 'new-access-token',
        expires_in: 3600,
        token_type: 'Bearer'
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => newTokens
      });

      const { result } = renderHook(() => useOAuthTokenManager());

      act(() => {
        // Manually set expired tokens
        result.current.tokens = expiredTokens;
      });

      const token = await act(async () => {
        return await result.current.getValidAccessToken();
      });

      expect(token).toBe('new-access-token');
      expect(fetch).toHaveBeenCalled();
    });

    it('should return null if no tokens available', async () => {
      const { result } = renderHook(() => useOAuthTokenManager());

      const token = await act(async () => {
        return await result.current.getValidAccessToken();
      });

      expect(token).toBeNull();
    });
  });

  describe('loading states', () => {
    it('should set loading state during refresh', async () => {
      (global.fetch as any).mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({
          ok: true,
          json: async () => ({ access_token: 'new-token', expires_in: 3600 })
        }), 100))
      );

      const { result } = renderHook(() => useOAuthTokenManager());

      act(() => {
        result.current.setTokens(mockTokens);
      });

      expect(result.current.isLoading).toBe(false);

      const refreshPromise = act(async () => {
        await result.current.refreshTokens();
      });

      expect(result.current.isLoading).toBe(true);

      await refreshPromise;

      expect(result.current.isLoading).toBe(false);
    });
  });
});