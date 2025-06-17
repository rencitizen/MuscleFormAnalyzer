'use client'

import { signIn, signOut, useSession } from 'next-auth/react'
import { useState } from 'react'
import { Button } from '../ui/button'
import { Alert, AlertDescription } from '../ui/alert'
import { Loader2 } from 'lucide-react'
import Image from 'next/image'

interface GoogleSignInProps {
  callbackUrl?: string
}

const GoogleSignIn: React.FC<GoogleSignInProps> = ({ callbackUrl = '/' }) => {
  const { data: session, status } = useSession()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSignIn = async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      // デバッグ情報を表示
      if (typeof window !== 'undefined' && (window as any).googleAuthDebugger) {
        console.log('Google Auth Debug Info:')
        ;(window as any).googleAuthDebugger.displayDebugInfo()
      }
      
      const result = await signIn('google', {
        callbackUrl,
        redirect: false
      })
      
      if (result?.error) {
        // エラーを診断
        if (typeof window !== 'undefined' && (window as any).googleAuthDebugger) {
          ;(window as any).googleAuthDebugger.diagnoseError({ error: result.error })
        }
        throw new Error(result.error)
      }
      
      // 成功した場合はリダイレクト
      if (result?.url) {
        window.location.href = result.url
      }
      
    } catch (error: any) {
      console.error('サインインエラー:', error)
      
      // エラーメッセージの日本語化
      const errorMessages: Record<string, string> = {
        'org_internal': 'このアプリは現在テスト段階です。アクセス権限をリクエストしてください。',
        'invalid_client': 'アプリケーションの設定に問題があります。開発者にお問い合わせください。',
        'redirect_uri_mismatch': 'リダイレクトURIの設定に問題があります。開発者にお問い合わせください。',
        'invalid_request': 'リクエストに問題があります。もう一度お試しください。',
        'access_denied': 'アクセスが拒否されました。',
        'OAuthSignin': 'Google認証の初期化に失敗しました。',
        'OAuthCallback': 'Google認証のコールバック処理に失敗しました。',
        'OAuthCreateAccount': 'アカウントの作成に失敗しました。',
        'EmailCreateAccount': 'メールアドレスの登録に失敗しました。',
        'Callback': 'コールバック処理中にエラーが発生しました。',
        'OAuthAccountNotLinked': 'このメールアドレスは既に別の方法で登録されています。',
        'SessionRequired': 'ログインが必要です。',
        'Default': 'サインインに失敗しました。もう一度お試しください。'
      }
      
      const errorKey = error.message || error.error || 'Default'
      setError(errorMessages[errorKey] || errorMessages['Default'])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSignOut = async () => {
    try {
      await signOut({ callbackUrl })
    } catch (error) {
      console.error('サインアウトエラー:', error)
    }
  }

  if (status === 'loading') {
    return (
      <div className="flex items-center justify-center p-4">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    )
  }

  if (session) {
    return (
      <div className="flex items-center gap-4">
        {session.user?.image && (
          <Image 
            src={session.user.image} 
            alt={session.user.name || 'User'}
            width={32}
            height={32}
            className="rounded-full"
          />
        )}
        <span className="text-sm font-medium">{session.user?.name}</span>
        <Button 
          onClick={handleSignOut}
          variant="outline"
          size="sm"
        >
          サインアウト
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      
      <Button
        onClick={handleSignIn}
        disabled={isLoading}
        variant="outline"
        className="w-full"
      >
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            サインイン中...
          </>
        ) : (
          <>
            <svg
              className="mr-2 h-4 w-4"
              aria-hidden="true"
              focusable="false"
              data-prefix="fab"
              data-icon="google"
              role="img"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 488 512"
            >
              <path
                fill="currentColor"
                d="M488 261.8C488 403.3 391.1 504 248 504 110.8 504 0 393.2 0 256S110.8 8 248 8c66.8 0 123 24.5 166.3 64.9l-67.5 64.9C258.5 52.6 94.3 116.6 94.3 256c0 86.5 69.1 156.6 153.7 156.6 98.2 0 135-70.4 140.8-106.9H248v-85.3h236.1c2.3 12.7 3.9 24.9 3.9 41.4z"
              />
            </svg>
            Googleでサインイン
          </>
        )}
      </Button>
      
      {/* デバッグモード */}
      {process.env.NODE_ENV === 'development' && (
        <div className="text-xs text-muted-foreground text-center">
          <button
            onClick={() => {
              if (typeof window !== 'undefined' && (window as any).googleAuthDebugger) {
                ;(window as any).googleAuthDebugger.displayDebugInfo()
              }
            }}
            className="underline hover:no-underline"
          >
            認証デバッグ情報を表示
          </button>
        </div>
      )}
    </div>
  )
}

export default GoogleSignIn