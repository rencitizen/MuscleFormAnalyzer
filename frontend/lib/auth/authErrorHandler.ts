/**
 * Enhanced OAuth Error Handler with Vercel-specific fixes
 */

export interface AuthErrorSolution {
  title: string
  steps: string[]
  urgency: 'critical' | 'warning' | 'info'
  estimatedTime: string
}

export const getVercelDomainFix = (currentDomain: string): AuthErrorSolution => {
  const isPreviewDomain = currentDomain.includes('-') && currentDomain.includes('.vercel.app')
  
  return {
    title: 'Vercel Domain Authorization Required',
    urgency: 'critical',
    estimatedTime: '10-15分',
    steps: [
      `Firebase Console設定:`,
      `1. https://console.firebase.google.com にアクセス`,
      `2. プロジェクトを選択 → Authentication → Settings → Authorized domains`,
      `3. "Add domain" をクリックして以下を追加:`,
      `   - ${currentDomain}`,
      '',
      `Google Cloud Console設定:`,
      `1. https://console.cloud.google.com にアクセス`,
      `2. APIs & Services → Credentials → OAuth 2.0 Client IDs`,
      `3. Web client を編集`,
      `4. Authorized JavaScript origins に追加:`,
      `   - https://${currentDomain}`,
      `5. Authorized redirect URIs に追加:`,
      `   - https://${currentDomain}/__/auth/handler`,
      `   - https://${currentDomain}/auth/callback`,
      '',
      `${isPreviewDomain ? '⚠️ 注意: これはプレビューURLです。本番デプロイ後は再設定が必要です。' : ''}`
    ]
  }
}

export const analyzeAuthError = (error: any): AuthErrorSolution | null => {
  const currentDomain = window.location.hostname
  const currentOrigin = window.location.origin
  
  // エラーコードによる詳細な解決策
  const errorSolutions: Record<string, AuthErrorSolution> = {
    'auth/unauthorized-domain': getVercelDomainFix(currentDomain),
    
    'auth/popup-blocked': {
      title: 'ポップアップブロック検出',
      urgency: 'warning',
      estimatedTime: '1分',
      steps: [
        'ブラウザのアドレスバーにあるポップアップブロックアイコンをクリック',
        `"${currentOrigin}" のポップアップを常に許可`,
        'ページを再読み込みして、もう一度ログインを試す'
      ]
    },
    
    'auth/operation-not-allowed': {
      title: 'Google認証が無効',
      urgency: 'critical',
      estimatedTime: '5分',
      steps: [
        'Firebase Console → Authentication → Sign-in method',
        'Googleプロバイダーを有効化',
        'プロジェクトのサポートメールを設定',
        '保存してから5分待つ'
      ]
    },
    
    'auth/invalid-api-key': {
      title: 'API Key設定エラー',
      urgency: 'critical',
      estimatedTime: '10分',
      steps: [
        'Vercel Dashboard → Project Settings → Environment Variables',
        'NEXT_PUBLIC_FIREBASE_API_KEY が正しく設定されているか確認',
        'Firebase Console → Project Settings → General → Web apps',
        'API Keyをコピーして、Vercelの環境変数を更新',
        'Redeployを実行'
      ]
    },
    
    'auth/configuration-not-found': {
      title: 'Firebase設定エラー',
      urgency: 'critical',
      estimatedTime: '15分',
      steps: [
        'すべてのFirebase環境変数を確認:',
        '- NEXT_PUBLIC_FIREBASE_API_KEY',
        '- NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN',
        '- NEXT_PUBLIC_FIREBASE_PROJECT_ID',
        '- NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET',
        '- NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID',
        '- NEXT_PUBLIC_FIREBASE_APP_ID',
        '',
        'Vercel Dashboardで上記すべてが設定されているか確認',
        '設定後、必ずRedeployを実行'
      ]
    }
  }
  
  // Error 400の特別処理
  if (error.message?.includes('Error 400') || error.message?.includes('invalid_request')) {
    return {
      title: 'Google OAuth Error 400 - Invalid Request',
      urgency: 'critical',
      estimatedTime: '20分',
      steps: [
        '🔴 これは通常、ドメイン承認の問題です',
        '',
        '即座に実行すべき手順:',
        `1. Firebase Console → Authorized domains に ${currentDomain} を追加`,
        `2. Google Cloud Console → OAuth 2.0 設定を更新`,
        `3. ブラウザのキャッシュとCookieをクリア`,
        `4. シークレットモードで再テスト`,
        '',
        '詳細な修正手順は上記の「Vercel Domain Authorization Required」を参照'
      ]
    }
  }
  
  return errorSolutions[error.code] || null
}

export const formatErrorMessage = (error: any): string => {
  const solution = analyzeAuthError(error)
  
  if (solution) {
    return `
🚨 ${solution.title}

修正手順 (推定時間: ${solution.estimatedTime}):
${solution.steps.map((step, i) => step ? `${step}` : '').join('\n')}

デバッグ情報:
- エラーコード: ${error.code}
- 現在のドメイン: ${window.location.hostname}
- 現在時刻: ${new Date().toLocaleString('ja-JP')}
    `.trim()
  }
  
  // デフォルトエラーメッセージ
  return `認証エラーが発生しました: ${error.message || error.code || 'Unknown error'}`
}

export const shouldRetryWithRedirect = (error: any): boolean => {
  const retryableCodes = [
    'auth/popup-blocked',
    'auth/popup-closed-by-user',
    'auth/cancelled-popup-request'
  ]
  
  return retryableCodes.includes(error.code) || 
         /iPhone|iPad|iPod|Android/i.test(navigator.userAgent)
}