'use client'

import { useState, useEffect } from 'react'
import { auth } from '../../lib/firebase'
import { getAuthDomains } from '../../lib/auth/googleAuthConfig'

interface ConfigCheckResult {
  name: string
  status: 'success' | 'error' | 'warning' | 'info'
  message: string
  fix?: string
}

export function OAuthDebugPanel() {
  const [checks, setChecks] = useState<ConfigCheckResult[]>([])
  const [isOpen, setIsOpen] = useState(false)
  const [loading, setLoading] = useState(false)

  const runDiagnostics = async () => {
    setLoading(true)
    const results: ConfigCheckResult[] = []
    
    // 1. ドメイン情報チェック
    const domains = getAuthDomains()
    results.push({
      name: '現在のドメイン',
      status: 'info',
      message: `${domains.currentDomain} (${domains.isVercel ? 'Vercel' : domains.isLocalhost ? 'Localhost' : 'その他'})`
    })

    results.push({
      name: '現在のOrigin',
      status: 'info',
      message: domains.currentOrigin
    })

    // 2. Firebase設定チェック
    const firebaseConfig = {
      apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
      authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
      projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
      storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
      messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
      appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID
    }

    // API Key存在チェック
    if (!firebaseConfig.apiKey) {
      results.push({
        name: 'Firebase API Key',
        status: 'error',
        message: '環境変数が設定されていません',
        fix: 'Vercel DashboardでNEXT_PUBLIC_FIREBASE_API_KEYを設定してください'
      })
    } else {
      results.push({
        name: 'Firebase API Key',
        status: 'success',
        message: `設定済み (${firebaseConfig.apiKey.substring(0, 10)}...)`
      })
    }

    // Auth Domain存在チェック
    if (!firebaseConfig.authDomain) {
      results.push({
        name: 'Firebase Auth Domain',
        status: 'error',
        message: '環境変数が設定されていません',
        fix: 'Vercel DashboardでNEXT_PUBLIC_FIREBASE_AUTH_DOMAINを設定してください'
      })
    } else {
      results.push({
        name: 'Firebase Auth Domain',
        status: 'success',
        message: firebaseConfig.authDomain
      })
    }

    // 3. 完全な設定チェック
    const allConfigsSet = Object.values(firebaseConfig).every(val => val !== undefined && val !== '')
    results.push({
      name: 'Firebase設定完全性',
      status: allConfigsSet ? 'success' : 'warning',
      message: allConfigsSet ? 'すべての環境変数が設定されています' : '一部の環境変数が未設定です',
      fix: allConfigsSet ? undefined : 'Vercel Dashboardですべての環境変数を確認してください'
    })

    // 4. Firebase Authインスタンスチェック
    try {
      if (auth) {
        results.push({
          name: 'Firebase Auth初期化',
          status: 'success',
          message: 'Authインスタンスが正常に初期化されています'
        })
      }
    } catch (error) {
      results.push({
        name: 'Firebase Auth初期化',
        status: 'error',
        message: 'Authインスタンスの初期化に失敗しました',
        fix: 'Firebase設定を確認してください'
      })
    }

    // 5. HTTPS接続チェック
    if (window.location.protocol !== 'https:' && !domains.isLocalhost) {
      results.push({
        name: 'HTTPS接続',
        status: 'warning',
        message: 'HTTPSではない接続です。OAuth認証はHTTPSが必要です',
        fix: 'HTTPSでアクセスしてください'
      })
    } else {
      results.push({
        name: 'HTTPS接続',
        status: 'success',
        message: domains.isLocalhost ? 'ローカル環境（HTTP許可）' : 'HTTPS接続'
      })
    }

    // 6. Vercel特有のドメインチェック
    if (domains.isVercel && domains.currentDomain.includes('-')) {
      results.push({
        name: 'Vercelドメイン形式',
        status: 'warning',
        message: 'プレビューデプロイメントURL検出。本番デプロイで異なるURLになる可能性があります',
        fix: 'カスタムドメインの使用を検討してください'
      })
    }

    // 7. 必要な設定URLリスト
    results.push({
      name: '必要なFirebase承認済みドメイン',
      status: 'info',
      message: domains.currentDomain,
      fix: `Firebase Console → Authentication → Settings → Authorized domainsに追加`
    })

    results.push({
      name: '必要なGoogle OAuth JavaScript origins',
      status: 'info',
      message: domains.currentOrigin,
      fix: `Google Cloud Console → APIs & Services → Credentials → OAuth 2.0 Client IDsに追加`
    })

    domains.redirectUris.forEach(uri => {
      results.push({
        name: '必要なGoogle OAuth Redirect URI',
        status: 'info',
        message: uri,
        fix: `Google Cloud Console → APIs & Services → Credentials → OAuth 2.0 Client IDsに追加`
      })
    })

    setChecks(results)
    setLoading(false)
  }

  useEffect(() => {
    if (isOpen) {
      runDiagnostics()
    }
  }, [isOpen])

  const statusColors = {
    success: 'text-green-600 bg-green-50',
    error: 'text-red-600 bg-red-50',
    warning: 'text-yellow-600 bg-yellow-50',
    info: 'text-blue-600 bg-blue-50'
  }

  const statusIcons = {
    success: '✓',
    error: '✗',
    warning: '⚠',
    info: 'ℹ'
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg hover:bg-blue-700 transition-colors"
        >
          OAuth診断ツール
        </button>
      )}

      {isOpen && (
        <div className="bg-white rounded-lg shadow-xl border border-gray-200 w-96 max-h-[80vh] overflow-hidden">
          <div className="bg-gray-100 px-4 py-3 border-b border-gray-200 flex justify-between items-center">
            <h3 className="font-semibold text-gray-800">OAuth設定診断</h3>
            <button
              onClick={() => setIsOpen(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>

          <div className="p-4 overflow-y-auto max-h-[calc(80vh-60px)]">
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-2 text-gray-600">診断中...</p>
              </div>
            ) : (
              <div className="space-y-3">
                {checks.map((check, index) => (
                  <div
                    key={index}
                    className={`p-3 rounded-lg ${statusColors[check.status]} border`}
                  >
                    <div className="flex items-start">
                      <span className="font-mono mr-2">{statusIcons[check.status]}</span>
                      <div className="flex-1">
                        <p className="font-medium">{check.name}</p>
                        <p className="text-sm mt-1">{check.message}</p>
                        {check.fix && (
                          <p className="text-xs mt-2 opacity-75">
                            修正方法: {check.fix}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}

                <div className="mt-4 pt-4 border-t border-gray-200">
                  <button
                    onClick={runDiagnostics}
                    className="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
                  >
                    再診断
                  </button>
                </div>

                <div className="mt-4 text-xs text-gray-500">
                  <p className="font-semibold mb-1">設定後の注意事項:</p>
                  <ul className="list-disc list-inside space-y-1">
                    <li>設定変更後、反映まで5-10分かかる場合があります</li>
                    <li>ブラウザのキャッシュをクリアしてください</li>
                    <li>シークレットモードでテストすることを推奨</li>
                  </ul>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}