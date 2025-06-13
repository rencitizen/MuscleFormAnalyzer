/**
 * Google OAuth設定ヘルパー
 * Error 400対策のための環境別設定
 */

export const getAuthDomains = () => {
  const currentDomain = typeof window !== 'undefined' ? window.location.hostname : '';
  const currentOrigin = typeof window !== 'undefined' ? window.location.origin : '';
  
  // Vercelデプロイメント検出
  const isVercel = currentDomain.includes('vercel.app');
  const isLocalhost = currentDomain === 'localhost' || currentDomain === '127.0.0.1';
  
  return {
    currentDomain,
    currentOrigin,
    isVercel,
    isLocalhost,
    requiredDomains: [
      'localhost',
      '*.vercel.app',
      currentDomain
    ],
    redirectUris: [
      `${currentOrigin}/__/auth/handler`,
      `${currentOrigin}/auth/callback`
    ]
  };
};

/**
 * Google Sign-in エラーの詳細診断
 */
export const diagnoseGoogleAuthError = (error: any) => {
  const domains = getAuthDomains();
  
  console.group('🔍 Google Auth Error Diagnosis');
  console.error('Error:', error);
  console.log('Error Code:', error.code);
  console.log('Error Message:', error.message);
  console.log('Current Domain:', domains.currentDomain);
  console.log('Current Origin:', domains.currentOrigin);
  console.log('Is Vercel:', domains.isVercel);
  console.log('Is Localhost:', domains.isLocalhost);
  console.log('Auth Domain:', process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN);
  console.groupEnd();
  
  // Error 400の一般的な原因
  if (error.message?.includes('Error 400') || error.code === 'auth/unauthorized-domain') {
    return {
      title: 'Google OAuth Error 400 - アクセスブロック',
      steps: [
        `1. Firebase Console → Authentication → Settings → Authorized domains で ${domains.currentDomain} を追加`,
        `2. Google Cloud Console → APIs & Services → Credentials → OAuth 2.0 Client IDs で設定:`,
        `   - Authorized JavaScript origins: ${domains.currentOrigin}`,
        `   - Authorized redirect URIs: ${domains.redirectUris.join(', ')}`,
        `3. 設定変更後、5-10分待ってから再試行`
      ],
      debugInfo: domains
    };
  }
  
  return null;
};

/**
 * PWA環境でのGoogle認証設定
 */
export const configurePWAGoogleAuth = () => {
  // PWAスタンドアロンモード検出
  const isPWA = window.matchMedia('(display-mode: standalone)').matches;
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
  
  if (isPWA) {
    console.log('PWA mode detected, using redirect method for Google Auth');
    return {
      preferRedirect: true,
      customParameters: {
        prompt: 'select_account',
        display: isIOS ? 'touch' : 'popup'
      }
    };
  }
  
  return {
    preferRedirect: false,
    customParameters: {
      prompt: 'select_account'
    }
  };
};