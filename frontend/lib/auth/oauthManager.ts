import { OAuthErrorHandler, TokenInfo } from './oauthErrorHandler';

export interface OAuthConfig {
  clientId: string;
  clientSecret?: string;
  redirectUri: string;
  scope: string;
  tokenEndpoint?: string;
  authEndpoint?: string;
}

export interface StoredTokens {
  access_token: string;
  refresh_token?: string;
  expires_at: number;
  scope?: string;
}

export class OAuthManager {
  private config: OAuthConfig;
  private retryCount = 0;
  private readonly maxRetries = 3;
  private readonly retryDelay = 1000;
  private tokenRefreshPromise: Promise<TokenInfo> | null = null;

  constructor(config: OAuthConfig) {
    this.config = {
      ...config,
      tokenEndpoint: config.tokenEndpoint || 'https://oauth2.googleapis.com/token',
      authEndpoint: config.authEndpoint || 'https://accounts.google.com/o/oauth2/v2/auth'
    };
  }

  async authenticate(): Promise<TokenInfo> {
    try {
      const existingTokens = this.getStoredTokens();
      
      if (existingTokens && this.isTokenValid(existingTokens)) {
        console.log('既存の有効なトークンを使用');
        return {
          access_token: existingTokens.access_token,
          expires_in: Math.floor((existingTokens.expires_at - Date.now()) / 1000),
          refresh_token: existingTokens.refresh_token,
          scope: existingTokens.scope
        };
      }

      if (existingTokens?.refresh_token) {
        console.log('リフレッシュトークンで更新を試行');
        try {
          const newTokens = await this.refreshAccessToken(existingTokens.refresh_token);
          return newTokens;
        } catch (refreshError) {
          console.error('リフレッシュ失敗:', refreshError);
          this.clearStoredTokens();
        }
      }

      console.log('完全な再認証が必要');
      return await this.initiateFullAuth();
      
    } catch (error) {
      if (this.retryCount < this.maxRetries) {
        this.retryCount++;
        console.log(`認証再試行 ${this.retryCount}/${this.maxRetries}`);
        await this.delay(this.retryDelay * this.retryCount);
        return this.authenticate();
      }
      
      throw error;
    }
  }

  async refreshAccessToken(refreshToken: string): Promise<TokenInfo> {
    if (this.tokenRefreshPromise) {
      console.log('既存のリフレッシュ処理を待機中');
      return this.tokenRefreshPromise;
    }

    this.tokenRefreshPromise = this.performTokenRefresh(refreshToken);
    
    try {
      const result = await this.tokenRefreshPromise;
      return result;
    } finally {
      this.tokenRefreshPromise = null;
    }
  }

  private async performTokenRefresh(refreshToken: string): Promise<TokenInfo> {
    if (!this.config.clientSecret) {
      throw new Error('Client secret is required for token refresh');
    }

    const params = new URLSearchParams({
      grant_type: 'refresh_token',
      refresh_token: refreshToken,
      client_id: this.config.clientId,
      client_secret: this.config.clientSecret
    });

    if (!this.config.tokenEndpoint) {
      throw new Error('Token endpoint is not configured');
    }

    const response = await fetch(this.config.tokenEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
      },
      body: params.toString()
    });

    const data = await response.json();

    if (!response.ok || data.error) {
      throw new Error(data.error_description || data.error || 'Token refresh failed');
    }

    const tokens: TokenInfo = {
      access_token: data.access_token,
      expires_in: data.expires_in,
      refresh_token: data.refresh_token || refreshToken,
      scope: data.scope,
      token_type: data.token_type
    };

    this.storeTokens(tokens);
    return tokens;
  }

  async exchangeCodeForTokens(code: string, state?: string): Promise<TokenInfo> {
    if (state && typeof window !== 'undefined') {
      const storedState = sessionStorage.getItem('oauth_state');
      if (!OAuthErrorHandler.validateState(state, storedState)) {
        throw new Error('State validation failed - possible CSRF attack');
      }
      sessionStorage.removeItem('oauth_state');
    }

    if (!this.config.clientSecret) {
      throw new Error('Client secret is required for code exchange');
    }

    const params = new URLSearchParams({
      grant_type: 'authorization_code',
      code,
      client_id: this.config.clientId,
      client_secret: this.config.clientSecret,
      redirect_uri: this.config.redirectUri
    });

    if (!this.config.tokenEndpoint) {
      throw new Error('Token endpoint is not configured');
    }

    const response = await fetch(this.config.tokenEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
      },
      body: params.toString()
    });

    const data = await response.json();

    if (!response.ok || data.error) {
      const error = OAuthErrorHandler.handleError(data);
      throw new Error(error.message);
    }

    const tokens: TokenInfo = {
      access_token: data.access_token,
      expires_in: data.expires_in,
      refresh_token: data.refresh_token,
      scope: data.scope,
      token_type: data.token_type
    };

    this.storeTokens(tokens);
    return tokens;
  }

  async validateCurrentToken(): Promise<boolean> {
    const tokens = this.getStoredTokens();
    if (!tokens) {
      return false;
    }

    if (!this.isTokenValid(tokens)) {
      if (tokens.refresh_token) {
        try {
          await this.refreshAccessToken(tokens.refresh_token);
          return true;
        } catch {
          return false;
        }
      }
      return false;
    }

    return await OAuthErrorHandler.checkTokenValidity(tokens.access_token);
  }

  initiateFullAuth(prompt?: 'none' | 'consent' | 'select_account'): Promise<TokenInfo> {
    return new Promise((resolve, reject) => {
      const authUrl = OAuthErrorHandler.buildAuthUrl({
        clientId: this.config.clientId,
        redirectUri: this.config.redirectUri,
        scope: this.config.scope,
        prompt: prompt || 'select_account',
        accessType: 'offline'
      });

      if (typeof window !== 'undefined') {
        window.location.href = authUrl;
      } else {
        reject(new Error('Authentication requires browser environment'));
      }
    });
  }

  getStoredTokens(): StoredTokens | null {
    if (typeof window === 'undefined') {
      return null;
    }

    try {
      const stored = localStorage.getItem('oauth_tokens');
      if (!stored) {
        return null;
      }

      const tokens: StoredTokens = JSON.parse(stored);
      return tokens;
    } catch (error) {
      console.error('Failed to retrieve stored tokens:', error);
      return null;
    }
  }

  private storeTokens(tokens: TokenInfo): void {
    if (typeof window === 'undefined') {
      return;
    }

    const storedTokens: StoredTokens = {
      access_token: tokens.access_token,
      refresh_token: tokens.refresh_token,
      expires_at: Date.now() + (tokens.expires_in * 1000),
      scope: tokens.scope
    };

    try {
      localStorage.setItem('oauth_tokens', JSON.stringify(storedTokens));
    } catch (error) {
      console.error('Failed to store tokens:', error);
    }
  }

  clearStoredTokens(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('oauth_tokens');
      sessionStorage.removeItem('oauth_state');
    }
  }

  private isTokenValid(tokens: StoredTokens): boolean {
    const bufferTime = 5 * 60 * 1000;
    return tokens.expires_at > (Date.now() + bufferTime);
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async revokeToken(token?: string): Promise<void> {
    const tokenToRevoke = token || this.getStoredTokens()?.access_token;
    
    if (!tokenToRevoke) {
      console.log('No token to revoke');
      return;
    }

    try {
      const response = await fetch('https://oauth2.googleapis.com/revoke', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `token=${tokenToRevoke}`
      });

      if (response.ok) {
        console.log('Token revoked successfully');
        this.clearStoredTokens();
      } else {
        console.error('Token revocation failed:', await response.text());
      }
    } catch (error) {
      console.error('Error revoking token:', error);
    }
  }
}