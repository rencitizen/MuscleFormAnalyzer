import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { OAuthManager } from '@/lib/auth/oauthManager';
import { OAuthError } from '@/lib/auth/oauthErrorHandler';

// Mock fetch
global.fetch = vi.fn();

// Mock window.location
delete (window as any).location;
window.location = { assign: vi.fn() } as any;

describe('OAuthManager', () => {
  let oauthManager: OAuthManager;

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    
    // Mock environment variables
    process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID = 'test-client-id';
    process.env.NEXT_PUBLIC_REDIRECT_URI = 'http://localhost:3000/auth/callback';
    
    oauthManager = new OAuthManager();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('initiateOAuthFlow', () => {
    it('should redirect to Google OAuth URL with correct parameters', () => {
      oauthManager.initiateOAuthFlow();

      expect(window.location.assign).toHaveBeenCalledWith(
        expect.stringContaining('https://accounts.google.com/o/oauth2/v2/auth')
      );
      expect(window.location.assign).toHaveBeenCalledWith(
        expect.stringContaining('client_id=test-client-id')
      );
      expect(window.location.assign).toHaveBeenCalledWith(
        expect.stringContaining('redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Fauth%2Fcallback')
      );
      expect(window.location.assign).toHaveBeenCalledWith(
        expect.stringContaining('response_type=code')
      );
      expect(window.location.assign).toHaveBeenCalledWith(
        expect.stringContaining('scope=openid%20profile%20email')
      );
    });

    it('should store state and code verifier in localStorage', () => {
      oauthManager.initiateOAuthFlow();

      const state = localStorage.getItem('oauth_state');
      const codeVerifier = localStorage.getItem('code_verifier');

      expect(state).toBeTruthy();
      expect(codeVerifier).toBeTruthy();
      expect(codeVerifier?.length).toBeGreaterThanOrEqual(43);
      expect(codeVerifier?.length).toBeLessThanOrEqual(128);
    });
  });

  describe('handleCallback', () => {
    const mockCode = 'test-auth-code';
    const mockState = 'test-state';
    const mockTokenResponse = {
      access_token: 'test-access-token',
      refresh_token: 'test-refresh-token',
      expires_in: 3600,
      token_type: 'Bearer',
      id_token: 'test-id-token'
    };

    beforeEach(() => {
      localStorage.setItem('oauth_state', mockState);
      localStorage.setItem('code_verifier', 'test-code-verifier');
    });

    it('should exchange authorization code for tokens', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockTokenResponse
      });

      const result = await oauthManager.handleCallback(mockCode, mockState);

      expect(fetch).toHaveBeenCalledWith(
        'https://oauth2.googleapis.com/token',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          body: expect.stringContaining(`code=${mockCode}`)
        })
      );

      expect(result).toEqual(mockTokenResponse);
    });

    it('should throw error if state does not match', async () => {
      await expect(
        oauthManager.handleCallback(mockCode, 'invalid-state')
      ).rejects.toThrow(OAuthError);
    });

    it('should throw error if state is missing from localStorage', async () => {
      localStorage.removeItem('oauth_state');

      await expect(
        oauthManager.handleCallback(mockCode, mockState)
      ).rejects.toThrow(OAuthError);
    });

    it('should handle token exchange failure', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        text: async () => 'Invalid grant'
      });

      await expect(
        oauthManager.handleCallback(mockCode, mockState)
      ).rejects.toThrow(OAuthError);
    });

    it('should clear OAuth state from localStorage after successful exchange', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockTokenResponse
      });

      await oauthManager.handleCallback(mockCode, mockState);

      expect(localStorage.getItem('oauth_state')).toBeNull();
      expect(localStorage.getItem('code_verifier')).toBeNull();
    });
  });

  describe('refreshAccessToken', () => {
    const mockRefreshToken = 'test-refresh-token';
    const mockNewTokenResponse = {
      access_token: 'new-access-token',
      expires_in: 3600,
      token_type: 'Bearer'
    };

    it('should refresh access token using refresh token', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockNewTokenResponse
      });

      const result = await oauthManager.refreshAccessToken(mockRefreshToken);

      expect(fetch).toHaveBeenCalledWith(
        'https://oauth2.googleapis.com/token',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          body: expect.stringContaining(`refresh_token=${mockRefreshToken}`)
        })
      );

      expect(result).toEqual(mockNewTokenResponse);
    });

    it('should handle refresh token failure', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
        text: async () => 'Invalid refresh token'
      });

      await expect(
        oauthManager.refreshAccessToken(mockRefreshToken)
      ).rejects.toThrow(OAuthError);
    });
  });

  describe('PKCE implementation', () => {
    it('should generate code verifier with correct length', () => {
      // Access private method through reflection for testing
      const generateCodeVerifier = (oauthManager as any).generateCodeVerifier.bind(oauthManager);
      const codeVerifier = generateCodeVerifier();

      expect(codeVerifier.length).toBeGreaterThanOrEqual(43);
      expect(codeVerifier.length).toBeLessThanOrEqual(128);
      expect(codeVerifier).toMatch(/^[A-Za-z0-9-._~]+$/);
    });

    it('should generate valid code challenge from code verifier', async () => {
      // Access private method through reflection for testing
      const generateCodeChallenge = (oauthManager as any).generateCodeChallenge.bind(oauthManager);
      const codeVerifier = 'test-code-verifier';
      const codeChallenge = await generateCodeChallenge(codeVerifier);

      expect(codeChallenge).toBeTruthy();
      expect(codeChallenge).toMatch(/^[A-Za-z0-9-_]+$/); // Base64URL characters
      expect(codeChallenge).not.toContain('='); // No padding
    });
  });
});