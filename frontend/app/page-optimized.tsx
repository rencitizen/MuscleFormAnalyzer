'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/components/providers/AuthProvider'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { 
  Camera, 
  Dumbbell, 
  Utensils,
  TrendingUp,
  Menu,
  Plus,
  ChevronRight
} from 'lucide-react'
import Link from 'next/link'
import { WelcomeModal } from '@/components/onboarding/WelcomeModal'

export default function OptimizedHomePage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [quickStats, setQuickStats] = useState({
    todayWorkout: false,
    lastFormScore: 0,
    weeklyProgress: 0,
    todayCalories: 0
  })

  useEffect(() => {
    if (!loading && !user) {
      router.push('/auth/login')
    }
  }, [user, loading, router])

  useEffect(() => {
    // ユーザーデータから統計を取得
    if (user) {
      // TODO: 実際のデータから取得
      setQuickStats({
        todayWorkout: false,
        lastFormScore: 88,
        weeklyProgress: 12,
        todayCalories: 1850
      })
    }
  }, [user])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">読み込み中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <WelcomeModal />
      
      {/* Simplified Header */}
      <header className="border-b bg-white/95 backdrop-blur sticky top-0 z-50">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Dumbbell className="w-6 h-6 text-primary" />
              <h1 className="text-lg font-bold">TENAX FIT</h1>
            </div>
            <Button variant="ghost" size="icon" className="md:hidden">
              <Menu className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6 max-w-lg">
        {/* Quick Actions - 最重要機能を大きく表示 */}
        <div className="mb-8">
          <h2 className="text-lg font-semibold mb-4">
            こんにちは、{user?.displayName?.split(' ')[0] || 'アスリート'}さん
          </h2>
          
          <div className="space-y-3">
            {/* Start Workout - 最も重要 */}
            <Card 
              className="bg-primary text-primary-foreground cursor-pointer hover:opacity-90 transition-opacity"
              onClick={() => router.push('/training')}
            >
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="bg-white/20 p-3 rounded-lg">
                      <Dumbbell className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg">トレーニング開始</h3>
                      <p className="text-sm opacity-90">
                        {quickStats.todayWorkout ? '今日2回目のトレーニング' : '今日のトレーニングを始める'}
                      </p>
                    </div>
                  </div>
                  <ChevronRight className="w-5 h-5" />
                </div>
              </CardContent>
            </Card>

            {/* Form Analysis */}
            <Card 
              className="cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => router.push('/analyze')}
            >
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="bg-blue-100 p-3 rounded-lg">
                      <Camera className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold">フォーム分析</h3>
                      <p className="text-sm text-muted-foreground">
                        前回スコア: {quickStats.lastFormScore}%
                      </p>
                    </div>
                  </div>
                  <ChevronRight className="w-5 h-5 text-muted-foreground" />
                </div>
              </CardContent>
            </Card>

            {/* Nutrition */}
            <Card 
              className="cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => router.push('/nutrition')}
            >
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="bg-green-100 p-3 rounded-lg">
                      <Utensils className="w-6 h-6 text-green-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold">食事記録</h3>
                      <p className="text-sm text-muted-foreground">
                        今日: {quickStats.todayCalories} kcal
                      </p>
                    </div>
                  </div>
                  <ChevronRight className="w-5 h-5 text-muted-foreground" />
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Quick Stats - シンプルに */}
        <div className="mb-8">
          <h3 className="text-sm font-medium text-muted-foreground mb-3">今週の進捗</h3>
          <div className="grid grid-cols-3 gap-3">
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-primary">
                  {quickStats.weeklyProgress}%
                </div>
                <p className="text-xs text-muted-foreground mt-1">目標達成率</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-blue-600">5</div>
                <p className="text-xs text-muted-foreground mt-1">トレーニング</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-green-600">
                  {quickStats.lastFormScore}
                </div>
                <p className="text-xs text-muted-foreground mt-1">平均スコア</p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Other Features - コンパクトに */}
        <div>
          <h3 className="text-sm font-medium text-muted-foreground mb-3">その他の機能</h3>
          <div className="grid grid-cols-2 gap-3">
            <Link href="/progress">
              <Card className="cursor-pointer hover:shadow-sm transition-shadow h-full">
                <CardContent className="p-4">
                  <TrendingUp className="w-5 h-5 text-purple-600 mb-2" />
                  <h4 className="text-sm font-medium">進捗確認</h4>
                </CardContent>
              </Card>
            </Link>
            <Link href="/exercises">
              <Card className="cursor-pointer hover:shadow-sm transition-shadow h-full">
                <CardContent className="p-4">
                  <Dumbbell className="w-5 h-5 text-orange-600 mb-2" />
                  <h4 className="text-sm font-medium">種目一覧</h4>
                </CardContent>
              </Card>
            </Link>
          </div>
        </div>
      </main>

      {/* Floating Action Button for mobile */}
      <div className="fixed bottom-6 right-6 md:hidden">
        <Button 
          size="lg" 
          className="rounded-full shadow-lg w-14 h-14"
          onClick={() => router.push('/training')}
        >
          <Plus className="w-6 h-6" />
        </Button>
      </div>
    </div>
  )
}