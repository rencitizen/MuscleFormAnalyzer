/**
 * Google OAuth認証のデバッグヘルパー
 * redirect_uri_mismatchエラーの診断と解決を支援
 */

export class GoogleAuthDebugger {
  private static instance: GoogleAuthDebugger;
  
  private constructor() {}
  
  static getInstance(): GoogleAuthDebugger {
    if (!this.instance) {
      this.instance = new GoogleAuthDebugger();
    }
    return this.instance;
  }

  /**
   * 現在の環境情報を取得
   */
  getEnvironmentInfo() {
    const isClient = typeof window !== 'undefined';
    const currentUrl = isClient ? window.location.origin : process.env.NEXTAUTH_URL || 'http://localhost:3000';
    const isVercel = process.env.VERCEL || process.env.NEXT_PUBLIC_VERCEL_URL;
    const isDevelopment = process.env.NODE_ENV === 'development';
    
    return {
      isClient,
      currentUrl,
      isVercel: !!isVercel,
      isDevelopment,
      vercelUrl: process.env.NEXT_PUBLIC_VERCEL_URL,
      nextAuthUrl: process.env.NEXTAUTH_URL,
    };
  }

  /**
   * 必要なredirect URIのリストを生成
   */
  getRequiredRedirectUris(): string[] {
    const env = this.getEnvironmentInfo();
    const baseUrls: string[] = [];
    
    // 開発環境
    if (env.isDevelopment) {
      baseUrls.push('http://localhost:3000');
    }
    
    // Vercel環境
    if (env.isVercel && env.vercelUrl) {
      baseUrls.push(`https://${env.vercelUrl}`);
    }
    
    // NEXTAUTH_URL環境変数
    if (env.nextAuthUrl) {
      baseUrls.push(env.nextAuthUrl);
    }
    
    // 現在のURL（クライアントサイド）
    if (env.isClient) {
      baseUrls.push(env.currentUrl);
    }
    
    // 重複を削除
    const uniqueUrls = [...new Set(baseUrls)];
    
    // 各URLに対してredirect URIを生成
    const redirectUris: string[] = [];
    uniqueUrls.forEach(url => {
      // NextAuth.js用
      redirectUris.push(`${url}/api/auth/callback/google`);
      
      // Firebase Auth用
      redirectUris.push(`${url}/__/auth/handler`);
      redirectUris.push(`${url}/auth/callback`);
    });
    
    return redirectUris;
  }

  /**
   * 環境変数の設定状態を確認
   */
  checkEnvironmentVariables() {
    const required = {
      // NextAuth関連
      NEXTAUTH_URL: process.env.NEXTAUTH_URL,
      NEXTAUTH_SECRET: process.env.NEXTAUTH_SECRET,
      
      // Google OAuth関連
      GOOGLE_CLIENT_ID: process.env.GOOGLE_CLIENT_ID,
      GOOGLE_CLIENT_SECRET: process.env.GOOGLE_CLIENT_SECRET,
      
      // Firebase関連（公開可能）
      NEXT_PUBLIC_FIREBASE_API_KEY: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
      NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
      NEXT_PUBLIC_FIREBASE_PROJECT_ID: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
    };
    
    const missing: string[] = [];
    const configured: string[] = [];
    
    Object.entries(required).forEach(([key, value]) => {
      if (!value) {
        missing.push(key);
      } else {
        configured.push(key);
      }
    });
    
    return {
      missing,
      configured,
      allConfigured: missing.length === 0,
    };
  }

  /**
   * デバッグ情報を表示
   */
  displayDebugInfo() {
    console.group('🔍 Google OAuth Debug Information');
    
    // 環境情報
    console.group('📍 Environment');
    const env = this.getEnvironmentInfo();
    console.table(env);
    console.groupEnd();
    
    // 環境変数チェック
    console.group('🔐 Environment Variables');
    const envCheck = this.checkEnvironmentVariables();
    if (envCheck.missing.length > 0) {
      console.error('❌ Missing variables:', envCheck.missing);
    }
    if (envCheck.configured.length > 0) {
      console.log('✅ Configured variables:', envCheck.configured);
    }
    console.groupEnd();
    
    // 必要なredirect URI
    console.group('🔗 Required Redirect URIs');
    const uris = this.getRequiredRedirectUris();
    console.log('Add these URIs to Google Cloud Console:');
    uris.forEach(uri => console.log(`  - ${uri}`));
    console.groupEnd();
    
    // 設定手順
    console.group('📋 Setup Instructions');
    console.log(`
1. Go to: https://console.cloud.google.com/apis/credentials
2. Select your OAuth 2.0 Client ID
3. Add all the redirect URIs listed above to:
   - Authorized JavaScript origins (base URLs only)
   - Authorized redirect URIs (full paths)
4. Save the changes
5. Wait 5-10 minutes for changes to propagate
    `);
    console.groupEnd();
    
    console.groupEnd();
  }

  /**
   * エラーの原因を診断
   */
  diagnoseError(error: any) {
    console.group('🚨 OAuth Error Diagnosis');
    
    if (error?.error === 'redirect_uri_mismatch' || error?.message?.includes('redirect_uri_mismatch')) {
      console.error('❌ Redirect URI Mismatch Error Detected');
      
      // 現在のredirect URIを推測
      const currentUrl = this.getEnvironmentInfo().currentUrl;
      console.log('📍 Current origin:', currentUrl);
      
      // 可能性のあるredirect URI
      console.log('🔗 Possible redirect URI being used:');
      console.log(`  - ${currentUrl}/api/auth/callback/google`);
      console.log(`  - ${currentUrl}/__/auth/handler`);
      
      // 解決策
      console.log('\n💡 Solution:');
      console.log('1. Run: googleAuthDebugger.displayDebugInfo()');
      console.log('2. Copy ALL redirect URIs from the output');
      console.log('3. Add them to Google Cloud Console');
      console.log('4. Check your .env.local file has all required variables');
    } else {
      console.error('❌ Unknown OAuth Error:', error);
    }
    
    console.groupEnd();
  }
}

// エクスポート
export const googleAuthDebugger = GoogleAuthDebugger.getInstance();

// グローバルに公開（デバッグ用）
if (typeof window !== 'undefined') {
  (window as any).googleAuthDebugger = googleAuthDebugger;
}