'use client'

import { useSearchParams } from 'next/navigation'
import { Suspense } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card'
import { Alert, AlertDescription, AlertTitle } from '../../../components/ui/alert'
import { AlertCircle, Home } from 'lucide-react'
import Link from 'next/link'
import { Button } from '../../../components/ui/button'

function ErrorContent() {
  const searchParams = useSearchParams()
  const error = searchParams.get('error')

  const errorDetails: Record<string, { title: string; description: string; action?: string }> = {
    Configuration: {
      title: 'サーバー設定エラー',
      description: 'サーバーの設定に問題があります。管理者にお問い合わせください。',
    },
    AccessDenied: {
      title: 'アクセス拒否',
      description: 'このリソースへのアクセス権限がありません。',
    },
    Verification: {
      title: '認証エラー',
      description: '認証トークンの検証に失敗しました。もう一度ログインしてください。',
    },
    OAuthSignin: {
      title: 'Google認証エラー',
      description: 'Google認証の開始に失敗しました。しばらく時間をおいてから再度お試しください。',
    },
    OAuthCallback: {
      title: 'コールバックエラー',
      description: 'Google認証のコールバック処理に失敗しました。',
      action: 'redirect_uri_mismatch エラーの場合は、開発者にお問い合わせください。',
    },
    OAuthCreateAccount: {
      title: 'アカウント作成エラー',
      description: 'Googleアカウントの作成に失敗しました。',
    },
    OAuthAccountNotLinked: {
      title: 'アカウント連携エラー',
      description: 'このメールアドレスは既に別の方法で登録されています。元の方法でログインしてください。',
    },
    Default: {
      title: '認証エラー',
      description: 'エラーが発生しました。もう一度お試しください。',
    },
  }

  const errorInfo = errorDetails[error || 'Default'] || errorDetails.Default

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl flex items-center justify-center gap-2">
            <AlertCircle className="h-6 w-6 text-destructive" />
            {errorInfo.title}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Alert variant="destructive">
            <AlertTitle>エラーの詳細</AlertTitle>
            <AlertDescription className="mt-2">
              {errorInfo.description}
              {errorInfo.action && (
                <p className="mt-2 text-sm">{errorInfo.action}</p>
              )}
            </AlertDescription>
          </Alert>
          
          {process.env.NODE_ENV === 'development' && error && (
            <div className="p-3 bg-muted rounded-md">
              <p className="text-xs font-mono">Error Code: {error}</p>
            </div>
          )}
          
          <div className="flex flex-col gap-2">
            <Link href="/auth/signin">
              <Button className="w-full" variant="default">
                もう一度ログインする
              </Button>
            </Link>
            
            <Link href="/">
              <Button className="w-full" variant="outline">
                <Home className="mr-2 h-4 w-4" />
                ホームに戻る
              </Button>
            </Link>
          </div>
          
          <div className="text-center text-xs text-muted-foreground">
            問題が解決しない場合は、管理者にお問い合わせください。
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default function ErrorPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    }>
      <ErrorContent />
    </Suspense>
  )
}