'use client';

import { useState } from 'react';
import { EnhancedGoogleSignIn } from '@/components/auth/EnhancedGoogleSignIn';
import { useOAuthTokenManager } from '@/hooks/useOAuthTokenManager';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';

export default function OAuthExamplePage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const {
    token,
    isValidating,
    isRefreshing,
    error,
    refreshToken,
    validateToken,
    clearTokens
  } = useOAuthTokenManager({
    config: {
      clientId: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID!,
      redirectUri: typeof window !== 'undefined' ? `${window.location.origin}/auth/callback` : '',
      scope: 'openid email profile'
    },
    autoRefresh: true,
    onTokenRefresh: (tokens) => {
      console.log('Token refreshed successfully');
      setIsAuthenticated(true);
    },
    onTokenExpired: () => {
      console.log('Token expired');
      setIsAuthenticated(false);
    },
    onError: (error) => {
      console.error('OAuth error:', error);
    }
  });

  const handleSignInSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleSignOut = () => {
    clearTokens();
    setIsAuthenticated(false);
  };

  const handleValidateToken = async () => {
    const isValid = await validateToken();
    if (isValid) {
      alert('トークンは有効です');
    } else {
      alert('トークンは無効です');
    }
  };

  return (
    <div className="container mx-auto py-8 max-w-4xl">
      <h1 className="text-3xl font-bold mb-8">OAuth認証の包括的な実装例</h1>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>認証状態</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span>認証状態:</span>
              <Badge variant={isAuthenticated ? 'default' : 'secondary'}>
                {isAuthenticated ? 'ログイン済み' : '未ログイン'}
              </Badge>
            </div>

            <div className="flex items-center justify-between">
              <span>トークン状態:</span>
              {token ? (
                <Badge variant="outline" className="flex items-center gap-1">
                  <CheckCircle className="h-3 w-3" />
                  有効
                </Badge>
              ) : (
                <Badge variant="outline" className="flex items-center gap-1">
                  <XCircle className="h-3 w-3" />
                  なし
                </Badge>
              )}
            </div>

            {isValidating && (
              <div className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm text-muted-foreground">検証中...</span>
              </div>
            )}

            {isRefreshing && (
              <div className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm text-muted-foreground">トークン更新中...</span>
              </div>
            )}

            {error && (
              <div className="p-3 bg-red-50 text-red-700 rounded-md text-sm">
                エラー: {error.message}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>認証アクション</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {!isAuthenticated ? (
              <EnhancedGoogleSignIn
                onSuccess={handleSignInSuccess}
                showDiagnostics={true}
              />
            ) : (
              <>
                <Button
                  onClick={handleValidateToken}
                  variant="outline"
                  className="w-full"
                  disabled={isValidating}
                >
                  {isValidating ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      検証中...
                    </>
                  ) : (
                    'トークンを検証'
                  )}
                </Button>

                <Button
                  onClick={() => refreshToken()}
                  variant="outline"
                  className="w-full"
                  disabled={isRefreshing}
                >
                  {isRefreshing ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      更新中...
                    </>
                  ) : (
                    'トークンを更新'
                  )}
                </Button>

                <Button
                  onClick={handleSignOut}
                  variant="destructive"
                  className="w-full"
                >
                  サインアウト
                </Button>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>実装のポイント</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 text-sm">
            <div>
              <h3 className="font-semibold mb-2">エラーハンドリング</h3>
              <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                <li>invalid_grant: 自動的に再認証を促す</li>
                <li>redirect_uri_mismatch: 詳細な設定手順を表示</li>
                <li>server_error: リトライ機能付き</li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-2">トークン管理</h3>
              <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                <li>自動更新: 有効期限の5分前に自動更新</li>
                <li>並行処理対策: 複数の更新リクエストを統合</li>
                <li>ストレージ: LocalStorageに暗号化して保存</li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-2">診断機能</h3>
              <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                <li>環境変数の検証</li>
                <li>リダイレクトURIの確認</li>
                <li>ネットワーク接続テスト</li>
                <li>システム時刻の同期確認</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}