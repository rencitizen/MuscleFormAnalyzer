'use client'

import { useEffect } from 'react'
import { useAnalytics, usePerformanceTracking } from '@/hooks/useAnalytics'
import { useABTest, ABTestComponent } from '@/utils/abtest'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

/**
 * アナリティクスとA/Bテストの実装例
 * このコンポーネントは、アナリティクストラッキングとA/Bテストの使用方法を示します
 */
export function AnalyticsExample() {
  const { track, trackFeatureUsage, trackError, identify } = useAnalytics()
  const { measurePerformance } = usePerformanceTracking()
  
  // A/Bテスト: ボタンカラー
  const { variant: buttonColor, trackConversion } = useABTest('cta_button_color')

  useEffect(() => {
    // ページビューは自動的にトラッキングされますが、
    // 特定のコンポーネントビューもトラッキング可能
    track('component_view', {
      component: 'AnalyticsExample',
      section: 'demo'
    })
  }, [track])

  // ボタンクリックハンドラー
  const handleButtonClick = async () => {
    // 機能使用をトラッキング
    trackFeatureUsage('demo_button', 'click', {
      button_variant: buttonColor,
      timestamp: new Date().toISOString()
    })

    // A/Bテストのコンバージョンを記録
    trackConversion('button_click')

    // パフォーマンスを計測しながら非同期処理を実行
    const performHeavyTask = measurePerformance('heavy_task', async () => {
      // 重い処理のシミュレーション
      await new Promise(resolve => setTimeout(resolve, 1000))
      return 'Task completed'
    })

    try {
      const result = await performHeavyTask()
      track('task_completed', { result })
    } catch (error) {
      trackError(error as Error, { context: 'heavy_task' })
    }
  }

  // ユーザー識別の例
  const handleUserLogin = (userId: string, email: string) => {
    identify(userId, {
      email,
      plan: 'premium',
      createdAt: new Date()
    })
    
    track('user_login', {
      method: 'email',
      success: true
    })
  }

  return (
    <div className="space-y-6">
      {/* A/Bテストコンポーネントの例 */}
      <ABTestComponent
        testId="onboarding_flow"
        control={
          <Card>
            <CardHeader>
              <CardTitle>従来のオンボーディング（コントロール）</CardTitle>
              <CardDescription>
                モーダルダイアログでチュートリアルを表示
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={() => track('onboarding_start', { type: 'modal' })}>
                チュートリアルを開始
              </Button>
            </CardContent>
          </Card>
        }
        treatment={
          <Card>
            <CardHeader>
              <CardTitle>新しいオンボーディング（テスト）</CardTitle>
              <CardDescription>
                インラインでステップバイステップのガイドを表示
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={() => track('onboarding_start', { type: 'inline' })}>
                ガイドを開始
              </Button>
            </CardContent>
          </Card>
        }
      />

      {/* ボタンカラーA/Bテストの例 */}
      <Card>
        <CardHeader>
          <CardTitle>A/Bテスト: ボタンカラー</CardTitle>
          <CardDescription>
            現在のバリアント: {buttonColor === 'blue' ? '青（コントロール）' : '緑（テスト）'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            onClick={handleButtonClick}
            className={buttonColor === 'blue' ? 'bg-blue-600 hover:bg-blue-700' : 'bg-green-600 hover:bg-green-700'}
          >
            アクションを実行
          </Button>
        </CardContent>
      </Card>

      {/* エラートラッキングの例 */}
      <Card>
        <CardHeader>
          <CardTitle>エラートラッキングの例</CardTitle>
          <CardDescription>
            エラーが発生した場合、自動的にトラッキングされます
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            variant="destructive"
            onClick={() => {
              try {
                throw new Error('テストエラー: これは意図的なエラーです')
              } catch (error) {
                trackError(error as Error, {
                  component: 'AnalyticsExample',
                  action: 'test_error_button'
                })
              }
            }}
          >
            エラーをテスト
          </Button>
        </CardContent>
      </Card>

      {/* カスタムイベントの例 */}
      <Card>
        <CardHeader>
          <CardTitle>カスタムイベントトラッキング</CardTitle>
          <CardDescription>
            ビジネス固有のイベントをトラッキング
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          <Button
            variant="outline"
            onClick={() => track('video_play', {
              video_id: 'demo_123',
              duration: 180,
              quality: '1080p'
            })}
          >
            動画再生をトラッキング
          </Button>
          
          <Button
            variant="outline"
            onClick={() => track('form_submit', {
              form_name: 'contact',
              fields_filled: 5,
              time_spent: 45
            })}
          >
            フォーム送信をトラッキング
          </Button>
          
          <Button
            variant="outline"
            onClick={() => track('share', {
              platform: 'twitter',
              content_type: 'article',
              content_id: 'abc123'
            })}
          >
            シェアをトラッキング
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}