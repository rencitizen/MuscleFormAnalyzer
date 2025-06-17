'use client'

import { useSearchParams } from 'next/navigation'
import { Suspense } from 'react'
import GoogleSignIn from '../../../components/auth/GoogleSignIn'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card'
import { Alert, AlertDescription } from '../../../components/ui/alert'
import { AlertCircle } from 'lucide-react'
import Link from 'next/link'
import { Button } from '../../../components/ui/button'

function SignInContent() {
  const searchParams = useSearchParams()
  const error = searchParams.get('error')
  const callbackUrl = searchParams.get('callbackUrl') || '/'

  const errorMessages: Record<string, string> = {
    Configuration: 'サーバー設定に問題があります。管理者にお問い合わせください。',
    AccessDenied: 'アクセスが拒否されました。',
    Verification: '認証トークンの検証に失敗しました。',
    OAuthSignin: 'Google認証の開始に失敗しました。',
    OAuthCallback: 'Google認証のコールバック処理に失敗しました。',
    OAuthCreateAccount: 'Googleアカウントの作成に失敗しました。',
    EmailCreateAccount: 'メールアカウントの作成に失敗しました。',
    Callback: '認証コールバックの処理中にエラーが発生しました。',
    OAuthAccountNotLinked: 'このメールアドレスは既に別の方法で登録されています。',
    EmailSignin: 'メール送信に失敗しました。',
    CredentialsSignin: 'ログイン情報が正しくありません。',
    SessionRequired: 'このページにアクセスするにはログインが必要です。',
    Default: 'エラーが発生しました。もう一度お試しください。',
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">MuscleFormAnalyzer</CardTitle>
          <CardDescription>
            アカウントにサインインしてください
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                {errorMessages[error] || errorMessages.Default}
              </AlertDescription>
            </Alert>
          )}
          
          <GoogleSignIn callbackUrl={callbackUrl} />
          
          <div className="text-center text-sm text-muted-foreground">
            <Link href="/" className="hover:underline">
              ホームに戻る
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default function SignInPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    }>
      <SignInContent />
    </Suspense>
  )
}