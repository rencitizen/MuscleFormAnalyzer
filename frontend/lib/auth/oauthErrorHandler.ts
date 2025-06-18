export interface OAuthError {
  error: string;
  error_description?: string;
  error_uri?: string;
}

export interface TokenInfo {
  access_token: string;
  expires_in: number;
  refresh_token?: string;
  scope?: string;
  token_type?: string;
}

export class OAuthErrorHandler {
  private static readonly ERROR_MESSAGES: Record<string, string> = {
    'invalid_request': '認証リクエストが無効です。パラメータを確認してください。',
    'invalid_client': 'クライアント認証に失敗しました。クライアントIDとシークレットを確認してください。',
    'invalid_grant': 'トークンが無効または期限切れです。再認証が必要です。',
    'unauthorized_client': 'クライアントが認証されていません。',
    'unsupported_grant_type': 'サポートされていない認証タイプです。',
    'invalid_scope': '無効なスコープが指定されました。',
    'access_denied': 'ユーザーがアクセスを拒否しました。',
    'server_error': 'サーバーエラーが発生しました。しばらく待ってから再試行してください。',
    'temporarily_unavailable': 'サービスが一時的に利用できません。',
    'redirect_uri_mismatch': 'リダイレクトURIが一致しません。設定を確認してください。'
  };

  static handleError(error: OAuthError | Error | string): {
    message: string;
    action: 'retry' | 'reauthenticate' | 'configure' | 'wait';
    details?: string;
  } {
    let errorCode: string;
    let errorDescription: string | undefined;

    if (typeof error === 'string') {
      errorCode = error;
    } else if ('error' in error) {
      errorCode = error.error;
      errorDescription = error.error_description;
    } else if (error instanceof Error) {
      errorCode = 'unknown_error';
      errorDescription = error.message;
    } else {
      errorCode = 'unknown_error';
    }

    const message = this.ERROR_MESSAGES[errorCode] || `未知のエラーが発生しました: ${errorCode}`;
    
    let action: 'retry' | 'reauthenticate' | 'configure' | 'wait';
    switch (errorCode) {
      case 'invalid_grant':
      case 'access_denied':
        action = 'reauthenticate';
        break;
      case 'redirect_uri_mismatch':
      case 'invalid_client':
      case 'unauthorized_client':
        action = 'configure';
        break;
      case 'server_error':
      case 'temporarily_unavailable':
        action = 'wait';
        break;
      default:
        action = 'retry';
    }

    return {
      message,
      action,
      details: errorDescription
    };
  }

  static async checkTokenValidity(accessToken: string): Promise<boolean> {
    try {
      const response = await fetch(
        `https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=${accessToken}`
      );
      
      if (!response.ok) {
        return false;
      }

      const tokenInfo = await response.json();
      
      if (tokenInfo.error) {
        console.error('Token validation error:', tokenInfo.error);
        return false;
      }

      const expiresIn = parseInt(tokenInfo.expires_in, 10);
      console.log(`Token expires in ${expiresIn} seconds`);
      
      return expiresIn > 60;
    } catch (error) {
      console.error('Token validation failed:', error);
      return false;
    }
  }

  static generateState(): string {
    return Array.from(crypto.getRandomValues(new Uint8Array(16)))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
  }

  static validateState(providedState: string, storedState: string | null): boolean {
    if (!storedState || !providedState) {
      console.error('State validation failed: missing state');
      return false;
    }

    if (providedState !== storedState) {
      console.error('State validation failed: state mismatch');
      return false;
    }

    return true;
  }

  static buildAuthUrl(params: {
    clientId: string;
    redirectUri: string;
    scope: string;
    state?: string;
    prompt?: 'none' | 'consent' | 'select_account';
    accessType?: 'online' | 'offline';
  }): string {
    const state = params.state || this.generateState();
    
    if (typeof window !== 'undefined') {
      sessionStorage.setItem('oauth_state', state);
    }

    const searchParams = new URLSearchParams({
      client_id: params.clientId,
      redirect_uri: params.redirectUri,
      scope: params.scope,
      response_type: 'code',
      state,
      access_type: params.accessType || 'offline',
      prompt: params.prompt || 'select_account'
    });

    return `https://accounts.google.com/o/oauth2/v2/auth?${searchParams.toString()}`;
  }

  static parseCallbackUrl(url: string): {
    code?: string;
    state?: string;
    error?: string;
    error_description?: string;
  } {
    const urlParams = new URLSearchParams(new URL(url).search);
    
    return {
      code: urlParams.get('code') || undefined,
      state: urlParams.get('state') || undefined,
      error: urlParams.get('error') || undefined,
      error_description: urlParams.get('error_description') || undefined
    };
  }

  static async diagnoseEnvironment(): Promise<{
    valid: boolean;
    issues: string[];
    recommendations: string[];
  }> {
    const issues: string[] = [];
    const recommendations: string[] = [];

    if (typeof window !== 'undefined') {
      const isLocalhost = window.location.hostname === 'localhost' || 
                         window.location.hostname === '127.0.0.1';
      const isHttps = window.location.protocol === 'https:';

      if (!isLocalhost && !isHttps) {
        issues.push('HTTPSが使用されていません');
        recommendations.push('本番環境ではHTTPSを使用してください');
      }

      try {
        const timeResponse = await fetch('https://worldtimeapi.org/api/timezone/Etc/UTC');
        const timeData = await timeResponse.json();
        const serverTime = new Date(timeData.datetime);
        const localTime = new Date();
        const timeDiff = Math.abs(serverTime.getTime() - localTime.getTime());
        
        if (timeDiff > 5 * 60 * 1000) {
          issues.push('システム時刻が5分以上ずれています');
          recommendations.push('システム時刻を同期してください');
        }
      } catch (error) {
        console.warn('時刻確認をスキップしました:', error);
      }
    }

    const requiredEnvVars = [
      'GOOGLE_CLIENT_ID',
      'GOOGLE_CLIENT_SECRET',
      'NEXTAUTH_URL',
      'NEXTAUTH_SECRET'
    ];

    if (typeof process !== 'undefined' && process.env) {
      requiredEnvVars.forEach(varName => {
        const envValue = process.env[varName as keyof typeof process.env];
        if (!envValue) {
          issues.push(`環境変数 ${varName} が設定されていません`);
          recommendations.push(`${varName} を .env.local ファイルに設定してください`);
        }
      });
    }

    return {
      valid: issues.length === 0,
      issues,
      recommendations
    };
  }
}