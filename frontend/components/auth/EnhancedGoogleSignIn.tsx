'use client';

import { useState, useEffect } from 'react';
import { signIn } from 'next-auth/react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, AlertCircle, RefreshCw } from 'lucide-react';
import { OAuthErrorHandler } from '@/lib/auth/oauthErrorHandler';
import { OAuthDiagnostics } from '@/lib/auth/oauthDiagnostics';
import { useToast } from '@/components/ui/use-toast';

interface EnhancedGoogleSignInProps {
  onSuccess?: () => void;
  onError?: (error: Error) => void;
  redirectTo?: string;
  showDiagnostics?: boolean;
}

export function EnhancedGoogleSignIn({
  onSuccess,
  onError,
  redirectTo = '/dashboard',
  showDiagnostics = false
}: EnhancedGoogleSignInProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showDetailedError, setShowDetailedError] = useState(false);
  const [diagnosticsRunning, setDiagnosticsRunning] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const error = urlParams.get('error');
    const errorDescription = urlParams.get('error_description');

    if (error) {
      handleOAuthError({ error, error_description: errorDescription });
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  const handleOAuthError = (oauthError: { error: string; error_description?: string | null }) => {
    const errorInfo = OAuthErrorHandler.handleError({
      error: oauthError.error,
      error_description: oauthError.error_description || undefined
    });

    setError(errorInfo.message);
    
    if (errorInfo.action === 'reauthenticate') {
      setTimeout(() => {
        setError(null);
        handleSignIn();
      }, 3000);
    } else if (errorInfo.action === 'configure') {
      setShowDetailedError(true);
    }

    onError?.(new Error(errorInfo.message));
  };

  const handleSignIn = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const state = OAuthErrorHandler.generateState();
      sessionStorage.setItem('oauth_state', state);

      const result = await signIn('google', {
        callbackUrl: redirectTo,
        redirect: true,
        state
      });

      if (result?.error) {
        throw new Error(result.error);
      }

      onSuccess?.();
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Sign in failed');
      setError(error.message);
      onError?.(error);
    } finally {
      setIsLoading(false);
    }
  };

  const runDiagnostics = async () => {
    setDiagnosticsRunning(true);
    try {
      const report = await OAuthDiagnostics.runFullDiagnostics();
      
      if (!report.canProceed) {
        toast({
          title: '設定に問題があります',
          description: report.recommendations[0] || '診断レポートを確認してください',
          variant: 'destructive'
        });
      } else {
        toast({
          title: '診断完了',
          description: '問題は検出されませんでした',
          variant: 'default'
        });
      }

      if (showDiagnostics) {
        const reportHtml = OAuthDiagnostics.generateHTMLReport(report);
        const reportWindow = window.open('', '_blank');
        if (reportWindow) {
          reportWindow.document.write(reportHtml);
          reportWindow.document.close();
        }
      }
    } catch (error) {
      toast({
        title: '診断エラー',
        description: '診断の実行中にエラーが発生しました',
        variant: 'destructive'
      });
    } finally {
      setDiagnosticsRunning(false);
    }
  };

  return (
    <div className="space-y-4">
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="space-y-2">
            <p>{error}</p>
            {showDetailedError && (
              <div className="mt-2 space-y-2">
                <p className="text-sm">以下を確認してください：</p>
                <ul className="text-sm list-disc list-inside">
                  <li>Google Cloud Console でクライアントIDが正しく設定されている</li>
                  <li>リダイレクトURIが正確に一致している</li>
                  <li>OAuth同意画面が設定されている</li>
                </ul>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={runDiagnostics}
                  disabled={diagnosticsRunning}
                >
                  {diagnosticsRunning ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      診断中...
                    </>
                  ) : (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4" />
                      診断を実行
                    </>
                  )}
                </Button>
              </div>
            )}
          </AlertDescription>
        </Alert>
      )}

      <Button
        onClick={handleSignIn}
        disabled={isLoading}
        className="w-full bg-white hover:bg-gray-100 text-gray-900 border border-gray-300"
      >
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
            サインイン中...
          </>
        ) : (
          <>
            <svg className="mr-2 h-5 w-5" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            Googleでサインイン
          </>
        )}
      </Button>

      {process.env.NODE_ENV === 'development' && (
        <div className="text-center">
          <Button
            variant="ghost"
            size="sm"
            onClick={runDiagnostics}
            disabled={diagnosticsRunning}
          >
            OAuth診断ツール
          </Button>
        </div>
      )}
    </div>
  );
}