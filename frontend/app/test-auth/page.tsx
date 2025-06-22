'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { auth } from '@/lib/firebase'
import { GoogleAuthProvider, signInWithPopup } from 'firebase/auth'

export default function TestAuthPage() {
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [windowLocation, setWindowLocation] = useState<{
    hostname: string
    protocol: string
    origin: string
    href: string
  } | null>(null)

  useEffect(() => {
    if (typeof window !== 'undefined') {
      setWindowLocation({
        hostname: window.location.hostname,
        protocol: window.location.protocol,
        origin: window.location.origin,
        href: window.location.href
      })
    }
  }, [])

  const testGoogleAuth = async () => {
    setLoading(true)
    setResult(null)
    setError(null)

    try {
      console.log('Starting Google Auth Test...')
      if (typeof window !== 'undefined') {
        console.log('Current URL:', window.location.href)
      }
      console.log('Firebase Config:', {
        apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY ? 'Set' : 'Not set',
        authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
        projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
      })

      const provider = new GoogleAuthProvider()
      const result = await signInWithPopup(auth, provider)
      
      setResult({
        user: {
          email: result.user.email,
          displayName: result.user.displayName,
          uid: result.user.uid,
        },
        credential: result.credential ? 'Present' : 'Not present',
      })
    } catch (err: any) {
      console.error('Auth Error:', err)
      setError({
        code: err.code,
        message: err.message,
        customData: err.customData,
        fullError: JSON.stringify(err, null, 2),
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen p-8">
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle>Google認証テストページ</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="p-4 bg-muted rounded-lg">
            <h3 className="font-semibold mb-2">現在の設定:</h3>
            <pre className="text-sm">
              {JSON.stringify({
                domain: windowLocation?.hostname || 'loading...',
                protocol: windowLocation?.protocol || 'loading...',
                origin: windowLocation?.origin || 'loading...',
                authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
                projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
              }, null, 2)}
            </pre>
          </div>

          <Button 
            onClick={testGoogleAuth} 
            disabled={loading}
            className="w-full"
          >
            {loading ? 'テスト中...' : 'Google認証をテスト'}
          </Button>

          {result && (
            <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <h3 className="font-semibold text-green-800 dark:text-green-200 mb-2">
                成功！
              </h3>
              <pre className="text-sm text-green-700 dark:text-green-300">
                {JSON.stringify(result, null, 2)}
              </pre>
            </div>
          )}

          {error && (
            <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
              <h3 className="font-semibold text-red-800 dark:text-red-200 mb-2">
                エラー:
              </h3>
              <div className="space-y-2 text-sm text-red-700 dark:text-red-300">
                <p><strong>コード:</strong> {error.code}</p>
                <p><strong>メッセージ:</strong> {error.message}</p>
                {error.customData && (
                  <div>
                    <strong>詳細データ:</strong>
                    <pre className="mt-1">{JSON.stringify(error.customData, null, 2)}</pre>
                  </div>
                )}
              </div>
              
              <div className="mt-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded">
                <h4 className="font-semibold text-yellow-800 dark:text-yellow-200 mb-1">
                  解決方法:
                </h4>
                <div className="text-sm text-yellow-700 dark:text-yellow-300">
                  {error.code === 'auth/unauthorized-domain' && windowLocation && (
                    <ol className="list-decimal list-inside space-y-1">
                      <li>Firebase Console → Authentication → Settings → Authorized domains</li>
                      <li>"{windowLocation.hostname}" を追加</li>
                      <li>Google Cloud Console → APIs & Services → Credentials</li>
                      <li>OAuth 2.0 Client IDsを編集</li>
                      <li>Authorized JavaScript origins: {windowLocation.origin}</li>
                      <li>Authorized redirect URIs: {windowLocation.origin}/__/auth/handler</li>
                    </ol>
                  )}
                  {error.code === 'auth/operation-not-allowed' && (
                    <ol className="list-decimal list-inside space-y-1">
                      <li>Firebase Console → Authentication → Sign-in method</li>
                      <li>Googleプロバイダーを有効化</li>
                      <li>プロジェクトのサポートメールを設定</li>
                    </ol>
                  )}
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}