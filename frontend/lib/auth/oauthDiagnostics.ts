import { OAuthErrorHandler } from './oauthErrorHandler';

export interface DiagnosticResult {
  category: string;
  status: 'success' | 'warning' | 'error';
  message: string;
  details?: string;
  action?: string;
}

export interface OAuthDiagnosticReport {
  timestamp: string;
  environment: string;
  diagnostics: DiagnosticResult[];
  recommendations: string[];
  canProceed: boolean;
}

export class OAuthDiagnostics {
  static async runFullDiagnostics(): Promise<OAuthDiagnosticReport> {
    const diagnostics: DiagnosticResult[] = [];
    const recommendations: string[] = [];
    let canProceed = true;

    diagnostics.push(...await this.checkEnvironmentVariables());
    diagnostics.push(...await this.checkRedirectUris());
    diagnostics.push(...await this.checkSystemTime());
    diagnostics.push(...await this.checkBrowserCompatibility());
    diagnostics.push(...await this.checkNetworkConnectivity());
    diagnostics.push(...await this.checkStorageAccess());

    diagnostics.forEach(diagnostic => {
      if (diagnostic.status === 'error') {
        canProceed = false;
      }
      if (diagnostic.action) {
        recommendations.push(diagnostic.action);
      }
    });

    return {
      timestamp: new Date().toISOString(),
      environment: this.detectEnvironment(),
      diagnostics,
      recommendations: [...new Set(recommendations)],
      canProceed
    };
  }

  private static detectEnvironment(): string {
    if (typeof window === 'undefined') {
      return 'server';
    }
    
    const hostname = window.location.hostname;
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return 'development';
    }
    if (hostname.includes('vercel.app')) {
      return 'vercel-preview';
    }
    return 'production';
  }

  private static async checkEnvironmentVariables(): Promise<DiagnosticResult[]> {
    const results: DiagnosticResult[] = [];
    
    if (typeof window !== 'undefined') {
      const publicVars: Record<string, string | undefined> = {
        'NEXT_PUBLIC_GOOGLE_CLIENT_ID': process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID,
        'NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN': process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
        'NEXT_PUBLIC_FIREBASE_PROJECT_ID': process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID
      };

      Object.entries(publicVars).forEach(([key, value]) => {
        if (!value) {
          results.push({
            category: '環境変数',
            status: 'error',
            message: `${key} が設定されていません`,
            action: `.env.local ファイルに ${key} を設定してください`
          });
        } else {
          results.push({
            category: '環境変数',
            status: 'success',
            message: `${key} が正しく設定されています`
          });
        }
      });
    }

    return results;
  }

  private static async checkRedirectUris(): Promise<DiagnosticResult[]> {
    const results: DiagnosticResult[] = [];
    
    if (typeof window !== 'undefined') {
      const currentOrigin = window.location.origin;
      const environment = this.detectEnvironment();
      
      const expectedUris = {
        'NextAuth.js': `${currentOrigin}/api/auth/callback/google`,
        'Firebase': `${currentOrigin}/__/auth/handler`,
        'Custom Callback': `${currentOrigin}/auth/callback`
      };

      results.push({
        category: 'リダイレクトURI',
        status: 'warning',
        message: `現在の環境: ${environment}`,
        details: `Origin: ${currentOrigin}`,
        action: 'Google Cloud Console で以下のURIが登録されていることを確認してください:\n' + 
                Object.entries(expectedUris).map(([name, uri]) => `- ${name}: ${uri}`).join('\n')
      });

      if (environment === 'production' && currentOrigin.startsWith('http:')) {
        results.push({
          category: 'セキュリティ',
          status: 'error',
          message: '本番環境でHTTPが使用されています',
          action: 'HTTPSを有効にしてください'
        });
      }
    }

    return results;
  }

  private static async checkSystemTime(): Promise<DiagnosticResult[]> {
    const results: DiagnosticResult[] = [];
    
    try {
      const response = await fetch('https://worldtimeapi.org/api/timezone/Etc/UTC');
      const data = await response.json();
      const serverTime = new Date(data.datetime);
      const localTime = new Date();
      const timeDiff = Math.abs(serverTime.getTime() - localTime.getTime());
      
      if (timeDiff > 5 * 60 * 1000) {
        results.push({
          category: 'システム時刻',
          status: 'error',
          message: `システム時刻が ${Math.floor(timeDiff / 60000)} 分ずれています`,
          details: `サーバー時刻: ${serverTime.toISOString()}, ローカル時刻: ${localTime.toISOString()}`,
          action: 'システム時刻を同期してください'
        });
      } else {
        results.push({
          category: 'システム時刻',
          status: 'success',
          message: 'システム時刻は正確です'
        });
      }
    } catch (error) {
      results.push({
        category: 'システム時刻',
        status: 'warning',
        message: '時刻同期の確認をスキップしました',
        details: error instanceof Error ? error.message : '不明なエラー'
      });
    }

    return results;
  }

  private static async checkBrowserCompatibility(): Promise<DiagnosticResult[]> {
    const results: DiagnosticResult[] = [];
    
    if (typeof window !== 'undefined') {
      if (!window.crypto || !window.crypto.getRandomValues) {
        results.push({
          category: 'ブラウザ互換性',
          status: 'error',
          message: 'Web Crypto API がサポートされていません',
          action: '最新のブラウザにアップデートしてください'
        });
      }

      if (!window.fetch) {
        results.push({
          category: 'ブラウザ互換性',
          status: 'error',
          message: 'Fetch API がサポートされていません',
          action: '最新のブラウザにアップデートしてください'
        });
      }

      const cookiesEnabled = navigator.cookieEnabled;
      if (!cookiesEnabled) {
        results.push({
          category: 'ブラウザ設定',
          status: 'error',
          message: 'Cookieが無効になっています',
          action: 'ブラウザの設定でCookieを有効にしてください'
        });
      }

      try {
        const testKey = '__oauth_storage_test__';
        localStorage.setItem(testKey, 'test');
        localStorage.removeItem(testKey);
        
        sessionStorage.setItem(testKey, 'test');
        sessionStorage.removeItem(testKey);
        
        results.push({
          category: 'ストレージ',
          status: 'success',
          message: 'ローカルストレージとセッションストレージが利用可能です'
        });
      } catch {
        results.push({
          category: 'ストレージ',
          status: 'error',
          message: 'ストレージアクセスが制限されています',
          action: 'プライベートブラウジングモードを無効にするか、ストレージを有効にしてください'
        });
      }
    }

    return results;
  }

  private static async checkNetworkConnectivity(): Promise<DiagnosticResult[]> {
    const results: DiagnosticResult[] = [];
    
    const endpoints = [
      { name: 'Google OAuth', url: 'https://accounts.google.com/.well-known/openid-configuration' },
      { name: 'Google APIs', url: 'https://www.googleapis.com/oauth2/v1/certs' }
    ];

    for (const endpoint of endpoints) {
      try {
        const response = await fetch(endpoint.url, { method: 'HEAD' });
        if (response.ok) {
          results.push({
            category: 'ネットワーク接続',
            status: 'success',
            message: `${endpoint.name} への接続が確認されました`
          });
        } else {
          results.push({
            category: 'ネットワーク接続',
            status: 'error',
            message: `${endpoint.name} への接続に失敗しました`,
            details: `Status: ${response.status}`,
            action: 'ネットワーク設定やファイアウォールを確認してください'
          });
        }
      } catch (error) {
        results.push({
          category: 'ネットワーク接続',
          status: 'error',
          message: `${endpoint.name} への接続エラー`,
          details: error instanceof Error ? error.message : '不明なエラー',
          action: 'インターネット接続を確認してください'
        });
      }
    }

    return results;
  }

  private static async checkStorageAccess(): Promise<DiagnosticResult[]> {
    const results: DiagnosticResult[] = [];
    
    if (typeof window !== 'undefined') {
      try {
        const testData = { test: 'data', timestamp: Date.now() };
        
        localStorage.setItem('__oauth_test__', JSON.stringify(testData));
        const retrieved = JSON.parse(localStorage.getItem('__oauth_test__') || '{}');
        localStorage.removeItem('__oauth_test__');
        
        if (retrieved.test === testData.test) {
          results.push({
            category: 'ストレージアクセス',
            status: 'success',
            message: 'LocalStorageへの読み書きが正常に動作しています'
          });
        } else {
          throw new Error('Storage verification failed');
        }
      } catch (error) {
        results.push({
          category: 'ストレージアクセス',
          status: 'error',
          message: 'LocalStorageへのアクセスに問題があります',
          details: error instanceof Error ? error.message : '不明なエラー',
          action: 'ブラウザのストレージ設定を確認してください'
        });
      }
    }

    return results;
  }

  static generateHTMLReport(report: OAuthDiagnosticReport): string {
    const statusColors = {
      success: '#22c55e',
      warning: '#f59e0b',
      error: '#ef4444'
    };

    const statusIcons = {
      success: '✓',
      warning: '⚠',
      error: '✗'
    };

    let html = `
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>OAuth診断レポート</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; background: #f3f4f6; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        h1 { color: #111827; margin-bottom: 20px; }
        .summary { background: #f9fafb; padding: 15px; border-radius: 6px; margin-bottom: 20px; }
        .diagnostic { margin-bottom: 15px; padding: 10px; border-left: 4px solid; border-radius: 4px; }
        .success { border-color: ${statusColors.success}; background: #f0fdf4; }
        .warning { border-color: ${statusColors.warning}; background: #fffbeb; }
        .error { border-color: ${statusColors.error}; background: #fef2f2; }
        .status-icon { display: inline-block; width: 20px; text-align: center; margin-right: 5px; }
        .details { margin-top: 5px; font-size: 0.9em; color: #6b7280; }
        .action { margin-top: 5px; font-size: 0.9em; color: #1f2937; background: #e5e7eb; padding: 5px 10px; border-radius: 3px; }
        .recommendations { margin-top: 20px; }
        .recommendation { background: #eff6ff; padding: 10px; margin-bottom: 10px; border-radius: 4px; border-left: 4px solid #3b82f6; }
    </style>
</head>
<body>
    <div class="container">
        <h1>OAuth診断レポート</h1>
        <div class="summary">
            <p><strong>実行日時:</strong> ${new Date(report.timestamp).toLocaleString('ja-JP')}</p>
            <p><strong>環境:</strong> ${report.environment}</p>
            <p><strong>ステータス:</strong> ${report.canProceed ? '✓ 認証を続行できます' : '✗ 問題を解決してから続行してください'}</p>
        </div>
        
        <h2>診断結果</h2>
        ${report.diagnostics.map(d => `
            <div class="diagnostic ${d.status}">
                <div>
                    <span class="status-icon" style="color: ${statusColors[d.status]}">${statusIcons[d.status]}</span>
                    <strong>${d.category}:</strong> ${d.message}
                </div>
                ${d.details ? `<div class="details">${d.details}</div>` : ''}
                ${d.action ? `<div class="action">対応: ${d.action}</div>` : ''}
            </div>
        `).join('')}
        
        ${report.recommendations.length > 0 ? `
            <div class="recommendations">
                <h2>推奨事項</h2>
                ${report.recommendations.map(r => `
                    <div class="recommendation">${r}</div>
                `).join('')}
            </div>
        ` : ''}
    </div>
</body>
</html>`;

    return html;
  }
}